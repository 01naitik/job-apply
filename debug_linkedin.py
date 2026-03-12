"""
debug_linkedin.py
-----------------
This script opens ONE job and prints all buttons found on the page
so we can see exactly what selectors to use.

Usage: python3 debug_linkedin.py
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

driver = get_driver()

# Step 1: Manual login
print("=" * 50)
print("👉 Please LOG IN to LinkedIn in the browser.")
print("⏳ You have 90 seconds...")
print("=" * 50)
driver.get("https://www.linkedin.com/login")
time.sleep(90)

# Step 2: Go to Easy Apply jobs in Berlin
print("\n🔍 Loading Easy Apply Frontend jobs in Berlin...")
driver.get(
    "https://www.linkedin.com/jobs/search/?"
    "keywords=Frontend%20Developer"
    "&location=Berlin%2C%20Germany"
    "&f_AL=true"   # Easy Apply only
    "&f_E=1,2"     # Entry level
    "&sortBy=DD"
)
time.sleep(5)

# Step 3: Print all job links found
print("\n📋 JOB LINKS FOUND:")
print("-" * 50)
all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
job_urls = []
for link in all_links:
    href = link.get_attribute("href")
    if href and href not in job_urls:
        job_urls.append(href.split("?")[0])
        print(f"  {href.split('?')[0]}")

print(f"\n  Total: {len(job_urls)} jobs found")

if not job_urls:
    print("\n❌ No jobs found! The page might not have loaded.")
    print("Current URL:", driver.current_url)
    driver.quit()
    exit()

# Step 4: Open first job and print ALL buttons
first_job = job_urls[0]
print(f"\n🔎 Opening first job: {first_job}")
driver.get(first_job)
time.sleep(5)

print("\n🔘 ALL BUTTONS ON THIS PAGE:")
print("-" * 50)
buttons = driver.find_elements(By.TAG_NAME, "button")
for i, btn in enumerate(buttons):
    try:
        text = btn.text.strip()
        aria = btn.get_attribute("aria-label") or ""
        classes = btn.get_attribute("class") or ""
        visible = btn.is_displayed()
        if text or aria:
            print(f"  [{i}] text='{text}' | aria-label='{aria}' | visible={visible}")
            print(f"       classes='{classes[:80]}'")
    except Exception:
        pass

print("\n🔗 ALL LINKS WITH 'apply' IN HREF OR TEXT:")
print("-" * 50)
links = driver.find_elements(By.TAG_NAME, "a")
for link in links:
    try:
        href = link.get_attribute("href") or ""
        text = link.text.strip()
        if "apply" in href.lower() or "apply" in text.lower():
            print(f"  text='{text}' | href='{href[:80]}'")
    except Exception:
        pass

print("\n✅ Debug complete! Copy everything above and send it.")
print("Press Ctrl+C to close.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    driver.quit()
