import os
import sys
import time

sys.path.append("/Users/getapp/PycharmProjects/book_scraper/.venv")
from stealth_scraper_ai import init_driver

driver = init_driver(instance_id=95, headless=False)
try:
    url = "https://violity.com/en/102141392-girejki-poslednih-tryoh-desyatkov-let-sucshestvovaniya-krymskogo-hanstva"
    print(f"Navigating to {url}")
    driver.get(url)
    time.sleep(8)
    
    title = driver.title
    print(f"Loaded Page Title: {title}")
    
    os.makedirs("/Users/getapp/PycharmProjects/book_scraper/scratch", exist_ok=True)
    screenshot_path = "/Users/getapp/PycharmProjects/book_scraper/scratch/violity_cf_test.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    # Print visible text
    body_text = driver.find_element("tag name", "body").text
    print(f"Body text snippet: {body_text[:1000]}")

finally:
    driver.quit()
