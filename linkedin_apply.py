"""
linkedin_apply.py - FINAL v4
-----------------------------
Fixes:
1. Terms & conditions dropdown now selects "Yes"
2. Applies to many different companies (deduplicates job links properly)
Usage: python3 linkedin_apply.py
"""

import time
import random
from config import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, ElementClickInterceptedException
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def pause(short=1.5, long=3.0):
    time.sleep(random.uniform(short, long))


def safe_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    pause(0.5, 1.0)
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def fill_text_field(field, value):
    field.clear()
    field.send_keys(value)
    pause(0.3, 0.7)


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    pause(1, 1.5)
    try:
        for c in driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'], main, .jobs-easy-apply-modal"):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", c)
    except Exception:
        pass


def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


def linkedin_login(driver):
    print("🔐 Opening LinkedIn login page...")
    driver.get("https://www.linkedin.com/login")
    print("👉 Please log in MANUALLY in the Chrome window now.")
    print("⏳ Waiting 90 seconds...")
    time.sleep(90)
    print("✅ Continuing...")


def search_jobs(driver):
    print("🔍 Searching Easy Apply Frontend jobs in Berlin...")
    driver.get(
        "https://www.linkedin.com/jobs/search/?"
        "keywords=Frontend%20Developer"
        "&location=Berlin%2C%20Germany"
        "&f_AL=true"
        "&f_E=1,2"
        "&sortBy=DD"
    )
    pause(4, 6)


def collect_job_links(driver, max_jobs=MAX_APPLIES):
    """Collect unique job links across multiple pages."""
    links = []
    seen_ids = set()
    page = 1

    while len(links) < max_jobs:
        print(f"  📄 Scanning page {page}...")
        pause(3, 4)

        all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
        for link in all_links:
            href = link.get_attribute("href")
            if not href:
                continue
            clean = href.split("?")[0].rstrip("/")
            # Extract job ID to deduplicate
            try:
                job_id = clean.split("/jobs/view/")[1].strip("/")
            except IndexError:
                continue
            if job_id not in seen_ids:
                seen_ids.add(job_id)
                links.append(clean)
            if len(links) >= max_jobs:
                break

        print(f"  ✅ {len(links)} unique jobs collected...")
        if len(links) >= max_jobs:
            break

        # Go to next page
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='View next page']")
            safe_click(driver, next_btn)
            pause(3, 5)
            page += 1
        except NoSuchElementException:
            # Try clicking next page number
            try:
                current = driver.find_element(By.CSS_SELECTOR, "li[data-test-pagination-page-btn].active, li.selected")
                next_li = current.find_element(By.XPATH, "following-sibling::li[1]")
                next_btn = next_li.find_element(By.TAG_NAME, "button")
                safe_click(driver, next_btn)
                pause(3, 5)
                page += 1
            except Exception:
                print("  📄 No more pages.")
                break

    print(f"  📋 Total unique jobs: {len(links)}")
    return links[:max_jobs]


def handle_all_dropdowns(driver):
    """
    Handle ALL dropdowns on the page.
    - Terms & conditions / agreement dropdowns → select Yes
    - Experience level dropdowns → select Entry/Junior
    - Any other required dropdowns → select first non-empty option
    """
    try:
        selects = driver.find_elements(By.TAG_NAME, "select")
        for sel in selects:
            try:
                if not sel.is_displayed():
                    continue
                s = Select(sel)

                # Get label for this select
                label_text = ""
                try:
                    sel_id = sel.get_attribute("id")
                    if sel_id:
                        lbl = driver.find_element(By.CSS_SELECTOR, f"label[for='{sel_id}']")
                        label_text = lbl.text.lower()
                except Exception:
                    pass

                options_text = [o.text.lower().strip() for o in s.options]
                current_val = s.first_selected_option.get_attribute("value") or ""

                # Skip if already has a real value selected
                if current_val and current_val not in ["", "select", "please select", "-1", "0"]:
                    continue

                print(f"    📋 Dropdown: '{label_text or 'unknown'}' | options: {options_text[:5]}")

                # TERMS & CONDITIONS / AGREEMENT / YES-NO dropdowns
                # These usually have Yes/No or Agree/Disagree options
                yes_keywords = ["yes", "agree", "accept", "ja", "i agree", "i accept"]
                matched_yes = next(
                    (o for o in options_text if any(k in o for k in yes_keywords)),
                    None
                )
                if matched_yes:
                    s.select_by_index(options_text.index(matched_yes))
                    print(f"    ✅ Selected '{matched_yes}' for agreement/terms dropdown")
                    continue

                # EXPERIENCE LEVEL dropdowns
                exp_keywords = ["entry", "junior", "0-1", "less than 1", "1 year", "associate"]
                matched_exp = next(
                    (o for o in options_text if any(k in o for k in exp_keywords)),
                    None
                )
                if matched_exp:
                    s.select_by_index(options_text.index(matched_exp))
                    print(f"    ✅ Selected '{matched_exp}' for experience dropdown")
                    continue

                # COUNTRY dropdowns
                if "country" in label_text or "nation" in label_text:
                    germany_match = next((o for o in options_text if "german" in o), None)
                    if germany_match:
                        s.select_by_index(options_text.index(germany_match))
                        print(f"    ✅ Selected Germany for country dropdown")
                        continue

                # DEFAULT: pick first non-empty, non-placeholder option
                for i, opt in enumerate(options_text):
                    if opt and opt not in ["select", "please select", "choose", "-- select --", ""]:
                        s.select_by_index(i)
                        print(f"    ✅ Selected '{opt}' (default first valid option)")
                        break

            except Exception as e:
                print(f"    ⚠️  Dropdown error: {e}")
                continue
    except Exception:
        pass


def fill_form_fields(driver, company_name, job_title_text):
    """Fill all visible form fields."""

    # Text / email / tel / number inputs
    inputs = driver.find_elements(
        By.CSS_SELECTOR,
        "input[type='text'], input[type='tel'], input[type='email'], input[type='number']"
    )
    for inp in inputs:
        try:
            if not inp.is_displayed() or not inp.is_enabled():
                continue
            val = inp.get_attribute("value") or ""
            if val.strip():
                continue

            label_text = ""
            try:
                lid = inp.get_attribute("id")
                if lid:
                    lbl = driver.find_element(By.CSS_SELECTOR, f"label[for='{lid}']")
                    label_text = lbl.text.lower()
            except NoSuchElementException:
                pass
            placeholder = (inp.get_attribute("placeholder") or "").lower()
            name_attr = (inp.get_attribute("name") or "").lower()
            combined = label_text + " " + placeholder + " " + name_attr

            if "first" in combined:
                fill_text_field(inp, FIRST_NAME)
            elif "last" in combined or "surname" in combined:
                fill_text_field(inp, LAST_NAME)
            elif "phone" in combined or "mobile" in combined or "tel" in combined:
                fill_text_field(inp, PHONE)
            elif "city" in combined or "location" in combined:
                fill_text_field(inp, CITY)
            elif "email" in combined:
                fill_text_field(inp, LINKEDIN_EMAIL)
            elif "year" in combined or "experience" in combined:
                fill_text_field(inp, "1")
            elif "salary" in combined:
                fill_text_field(inp, "35000")
            elif "linkedin" in combined or "profile" in combined:
                fill_text_field(inp, f"https://www.linkedin.com/in/{FIRST_NAME.lower()}-{LAST_NAME.lower()}")
        except Exception:
            continue

    # CV Upload
    try:
        for fi in driver.find_elements(By.CSS_SELECTOR, "input[type='file']"):
            try:
                fi.send_keys(CV_PATH)
                pause(1, 2)
                print("    📎 CV uploaded!")
            except Exception:
                pass
    except Exception:
        pass

    # Textareas (cover letter)
    try:
        for ta in driver.find_elements(By.TAG_NAME, "textarea"):
            try:
                if not ta.is_displayed():
                    continue
                if not (ta.get_attribute("value") or ta.text or "").strip():
                    cover = COVER_LETTER.format(
                        job_title=job_title_text,
                        company=company_name,
                        full_name=f"{FIRST_NAME} {LAST_NAME}"
                    )
                    fill_text_field(ta, cover)
                    print("    📝 Cover letter filled!")
            except Exception:
                continue
    except Exception:
        pass

    # Checkboxes — tick any agreement/terms checkboxes
    try:
        for cb in driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"):
            try:
                if cb.is_displayed() and not cb.is_selected():
                    # Check label to see if it's a terms/agreement checkbox
                    label_text = ""
                    try:
                        lid = cb.get_attribute("id")
                        if lid:
                            lbl = driver.find_element(By.CSS_SELECTOR, f"label[for='{lid}']")
                            label_text = lbl.text.lower()
                    except Exception:
                        pass
                    if any(k in label_text for k in ["agree", "terms", "condition", "policy", "consent"]):
                        safe_click(driver, cb)
                        print("    ✅ Ticked agreement checkbox!")
            except Exception:
                continue
    except Exception:
        pass

    # Radio buttons — prefer Yes
    try:
        for radio in driver.find_elements(By.CSS_SELECTOR, "input[type='radio']"):
            try:
                val = (radio.get_attribute("value") or "").lower()
                if val in ["yes", "true", "1"] and not radio.is_selected():
                    safe_click(driver, radio)
            except Exception:
                continue
    except Exception:
        pass

    # ALL dropdowns — handled separately with smart logic
    handle_all_dropdowns(driver)


def find_action_button(driver):
    """Find and click Next / Review / Submit. Returns 'submitted', 'next', or 'stuck'."""
    scroll_to_bottom(driver)
    pause(1, 1.5)

    search_roots = []
    try:
        modal = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
        search_roots.append(modal)
    except NoSuchElementException:
        pass
    search_roots.append(driver)

    for root in search_roots:
        try:
            buttons = root.find_elements(By.TAG_NAME, "button")
        except Exception:
            continue

        # Submit first
        for btn in buttons:
            try:
                if not btn.is_displayed() or not btn.is_enabled():
                    continue
                combined = ((btn.text or "") + " " + (btn.get_attribute("aria-label") or "")).lower()
                if "submit application" in combined or ("submit" in combined and "application" in combined):
                    safe_click(driver, btn)
                    print("    🎉 Clicked SUBMIT!")
                    return "submitted"
            except Exception:
                continue

        # Next / Review / Continue
        for btn in buttons:
            try:
                if not btn.is_displayed() or not btn.is_enabled():
                    continue
                combined = ((btn.text or "") + " " + (btn.get_attribute("aria-label") or "")).lower()
                if any(w in combined for w in ["review your application", "continue to next", "next", "continue", "save and continue"]):
                    safe_click(driver, btn)
                    print(f"    ➡️  Clicked: '{btn.text.strip()}'")
                    return "next"
            except Exception:
                continue

    return "stuck"


def apply_to_job_url(driver, job_url):
    driver.get(job_url)
    pause(3, 5)

    # Get title and company
    job_title_text = JOB_TITLE
    company_name = "the company"
    try:
        job_title_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        ).text.strip()
    except TimeoutException:
        pass
    for sel in ["a[href*='/company/']", ".job-details-jobs-unified-top-card__company-name a"]:
        try:
            t = driver.find_element(By.CSS_SELECTOR, sel).text.strip()
            if t:
                company_name = t
                break
        except NoSuchElementException:
            continue

    print(f"\n  📝 {job_title_text} @ {company_name}")

    # Find Easy Apply element
    easy_apply_el = None
    apply_url = None

    try:
        easy_apply_el = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href*='apply'][href*='openSDUIApplyFlow']")
            )
        )
        apply_url = easy_apply_el.get_attribute("href")
        print("    🎯 Found Easy Apply link!")
    except TimeoutException:
        pass

    if not easy_apply_el:
        try:
            for link in driver.find_elements(By.TAG_NAME, "a"):
                if "easy apply" in (link.text or "").lower():
                    easy_apply_el = link
                    apply_url = link.get_attribute("href")
                    print("    🎯 Found Easy Apply by text!")
                    break
        except Exception:
            pass

    if not easy_apply_el:
        try:
            for btn in driver.find_elements(By.TAG_NAME, "button"):
                combined = ((btn.text or "") + (btn.get_attribute("aria-label") or "")).lower()
                if "easy apply" in combined:
                    easy_apply_el = btn
                    print("    🎯 Found Easy Apply button!")
                    break
        except Exception:
            pass

    if not easy_apply_el:
        print("  ⏭  No Easy Apply found — skipping.")
        return False

    # Navigate directly to apply URL if available, otherwise click
    if apply_url and "apply" in apply_url:
        print(f"    🌐 Navigating to apply page...")
        driver.get(apply_url)
    else:
        safe_click(driver, easy_apply_el)

    pause(4, 5)
    current_url = driver.current_url
    print(f"    📍 Now on: {current_url[:70]}...")

    # Check we're on an apply page
    on_apply_page = any(k in current_url for k in ["apply", "checkpoint", "submit"])
    modal_open = False
    try:
        driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
        modal_open = True
    except NoSuchElementException:
        pass

    if not on_apply_page and not modal_open:
        print("    ⚠️  Apply page did not load — skipping.")
        return False

    print("    ✅ Apply page loaded! Starting form fill...")

    max_steps = 20
    stuck_count = 0

    for step in range(max_steps):
        pause(2, 3)
        print(f"    📋 Step {step + 1}...")

        fill_form_fields(driver, company_name, job_title_text)
        result = find_action_button(driver)

        if result == "submitted":
            print(f"  ✅ APPLIED to {job_title_text} at {company_name}!")
            pause(2, 3)
            try:
                dismiss = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
                safe_click(driver, dismiss)
            except NoSuchElementException:
                pass
            return True

        elif result == "stuck":
            stuck_count += 1
            if stuck_count >= 2:
                print(f"  ⚠️  Stuck — skipping this job.")
                for label in ["Dismiss", "Close", "Cancel"]:
                    try:
                        btn = driver.find_element(By.CSS_SELECTOR, f"button[aria-label='{label}']")
                        safe_click(driver, btn)
                        pause(1)
                        try:
                            discard = driver.find_element(By.CSS_SELECTOR, "button[data-test-dialog-primary-btn]")
                            safe_click(driver, discard)
                        except NoSuchElementException:
                            pass
                        break
                    except NoSuchElementException:
                        continue
                return False
            print("    ⏳ Retrying...")
            pause(3, 4)
        else:
            stuck_count = 0
            pause(2, 3)

    return False


if __name__ == "__main__":
    driver = get_driver()
    applied = 0
    skipped = 0

    try:
        linkedin_login(driver)
        search_jobs(driver)
        job_links = collect_job_links(driver, max_jobs=MAX_APPLIES)

        print(f"\n🚀 Starting applications for {len(job_links)} jobs...\n")

        for url in job_links:
            if applied >= MAX_APPLIES:
                break
            success = apply_to_job_url(driver, url)
            if success:
                applied += 1
                print(f"  📊 Progress: {applied}/{MAX_APPLIES} applications sent")
            else:
                skipped += 1
            pause(2, 4)

    except KeyboardInterrupt:
        print("\n⛔ Stopped by user.")
    finally:
        driver.quit()
        print(f"\n🎉 Done! Applied: {applied} | Skipped: {skipped}")
        print("👋 Browser closed.")