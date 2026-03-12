"""
stepstone_apply.py
------------------
Automatically applies to entry-level Frontend Developer jobs on StepStone.de.
StepStone does not have a universal "one-click apply" like LinkedIn Easy Apply,
so this script:
  1. Searches for matching jobs
  2. Opens each job listing
  3. Clicks "Jetzt bewerben" (Apply now)
  4. Fills the application form where possible
  5. Uploads your CV
  6. Submits the application

Usage:  python3 stepstone_apply.py
"""

import time
import random
import os
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


# ── helpers ─────────────────────────────────────────────────────────────────

def pause(short=1.5, long=3.0):
    time.sleep(random.uniform(short, long))


def safe_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    pause(0.5, 1.0)
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def fill_field(field, value):
    field.clear()
    field.send_keys(value)
    pause(0.3, 0.6)


def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    # Disable automation detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


# ── login ────────────────────────────────────────────────────────────────────

def stepstone_login(driver):
    print("🔐 Logging into StepStone...")
    driver.get("https://www.stepstone.de/candidate/login")
    wait = WebDriverWait(driver, 15)

    try:
        # Accept cookies if banner appears
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id*='accept'], button[data-testid*='cookie-accept']"))
        )
        cookie_btn.click()
        pause(1, 2)
    except TimeoutException:
        pass

    try:
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']")))
        fill_field(email_field, STEPSTONE_EMAIL)

        pw_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        fill_field(pw_field, STEPSTONE_PASSWORD)

        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        safe_click(driver, login_btn)
        pause(3, 5)
        print("✅ Logged into StepStone!")
    except Exception as e:
        print(f"⚠️  Login issue: {e}. Continuing without login — will try to apply as guest.")


# ── search jobs ──────────────────────────────────────────────────────────────

def search_jobs(driver):
    keywords = STEPSTONE_KEYWORDS.replace(" ", "+")
    location = STEPSTONE_LOCATION.replace(" ", "+")
    search_url = (
        f"https://www.stepstone.de/jobs/{keywords}/in-{location}.html"
        f"?radius=30&where={location}&what={keywords}"
    )
    print(f"🔍 Searching StepStone: {STEPSTONE_KEYWORDS} in {STEPSTONE_LOCATION}...")
    driver.get(search_url)
    pause(3, 5)

    # Accept cookies if banner appears
    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Alle akzeptieren') or contains(text(),'Accept')]"))
        )
        cookie_btn.click()
        pause(1, 2)
    except TimeoutException:
        pass


# ── collect job links ────────────────────────────────────────────────────────

def collect_job_links(driver, max_jobs=MAX_APPLIES):
    links = []
    page = 1
    while len(links) < max_jobs:
        try:
            job_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "article[data-at='job-item'] a, a[data-at='job-item-title']")
                )
            )
            for card in job_cards:
                href = card.get_attribute("href")
                if href and "stepstone.de" in href and href not in links:
                    links.append(href)
                if len(links) >= max_jobs:
                    break
        except TimeoutException:
            print(f"  ⚠️  Could not load page {page}")
            break

        # Next page
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a[data-at='pagination-next'], a[aria-label='Nächste Seite']")
            safe_click(driver, next_btn)
            pause(3, 4)
            page += 1
        except NoSuchElementException:
            break

    print(f"  📋 Found {len(links)} job listings")
    return links[:max_jobs]


# ── apply to a single job ────────────────────────────────────────────────────

def apply_to_job(driver, job_url):
    driver.get(job_url)
    pause(2, 4)
    wait = WebDriverWait(driver, 10)

    # Get job title for cover letter
    try:
        job_title_text = driver.find_element(
            By.CSS_SELECTOR, "h1[data-at='header-job-title'], h1.listing-content-provider--title"
        ).text.strip()
        company_name = driver.find_element(
            By.CSS_SELECTOR, "a[data-at='header-company-name'], .listing-content-provider--name"
        ).text.strip()
    except NoSuchElementException:
        job_title_text = JOB_TITLE
        company_name = "the company"

    print(f"\n  📝 Applying: {job_title_text} @ {company_name}")

    # Click Apply button
    try:
        apply_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR,
             "button[data-at='apply-button'], a[data-at='apply-button'], "
             "button[data-genesis-element='BASE_BUTTON']")
        ))
        safe_click(driver, apply_btn)
        pause(2, 4)
    except TimeoutException:
        print(f"  ⚠️  No apply button found for {job_title_text} — skipping.")
        return False

    # Switch to new tab if opened
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        pause(2, 3)

    # Fill form fields
    try:
        form_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='tel']")
        for field in form_fields:
            name_attr = (field.get_attribute("name") or "").lower()
            placeholder = (field.get_attribute("placeholder") or "").lower()
            label_text = name_attr + " " + placeholder
            val = field.get_attribute("value") or ""
            if val.strip():
                continue

            if "first" in label_text or "vorname" in label_text:
                fill_field(field, FIRST_NAME)
            elif "last" in label_text or "nachname" in label_text or "name" in label_text:
                fill_field(field, LAST_NAME)
            elif "phone" in label_text or "telefon" in label_text or "mobil" in label_text:
                fill_field(field, PHONE)
            elif "email" in label_text or "e-mail" in label_text:
                fill_field(field, STEPSTONE_EMAIL)
            elif "city" in label_text or "ort" in label_text or "stadt" in label_text:
                fill_field(field, CITY)
    except Exception as e:
        print(f"  ⚠️  Form fill issue: {e}")

    # Upload CV
    try:
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        for fi in file_inputs:
            if os.path.exists(CV_PATH):
                fi.send_keys(CV_PATH)
                pause(2, 3)
    except Exception as e:
        print(f"  ⚠️  CV upload issue: {e}")

    # Cover letter textarea
    try:
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for ta in textareas:
            if not ta.get_attribute("value") and not ta.text.strip():
                cover = COVER_LETTER.format(
                    job_title=job_title_text,
                    company=company_name,
                    full_name=f"{FIRST_NAME} {LAST_NAME}"
                )
                fill_field(ta, cover)
    except Exception:
        pass

    # Submit
    try:
        submit_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR,
             "button[type='submit'], button[data-at='submit-button'], "
             "input[type='submit']")
        ))
        safe_click(driver, submit_btn)
        pause(2, 3)
        print(f"  ✅ Applied to {job_title_text} at {company_name}!")

        # Close extra tab if opened
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        return True
    except TimeoutException:
        print(f"  ⚠️  Could not find submit button — skipping.")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False


# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    driver = get_driver()
    applied = 0
    skipped = 0

    try:
        stepstone_login(driver)
        search_jobs(driver)
        job_links = collect_job_links(driver, max_jobs=MAX_APPLIES)

        for url in job_links:
            if applied >= MAX_APPLIES:
                break
            success = apply_to_job(driver, url)
            if success:
                applied += 1
                print(f"  📊 Progress: {applied}/{MAX_APPLIES}")
            else:
                skipped += 1
            pause(2, 4)

    except KeyboardInterrupt:
        print("\n⛔ Stopped by user.")
    finally:
        driver.quit()
        print(f"\n🎉 StepStone Done! Applied: {applied} | Skipped: {skipped}")
