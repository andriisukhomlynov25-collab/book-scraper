import os
import sys
import time

sys.path.append("/Users/getapp/PycharmProjects/book_scraper/.venv")
from stealth_scraper_ai import init_driver

driver = init_driver(instance_id=94, headless=False)
try:
    url = "https://violity.com/ru/111423016-lyubavskij-m-k-ocherk-istorii-litovsko-russkogo-gosudarstva-do-lyublinskoj-unii"
    print(f"Navigating to {url}")
    driver.get(url)
    time.sleep(8)
    
    title = driver.title
    print(f"Loaded Page Title: {title}")
    print(f"Current URL in Browser: {driver.current_url}")
    
    os.makedirs("/Users/getapp/PycharmProjects/book_scraper/scratch", exist_ok=True)
    screenshot_path = "/Users/getapp/PycharmProjects/book_scraper/scratch/violity_load_test_111423016.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    # Print visible text
    body_text = driver.find_element("tag name", "body").text
    print(f"Body text snippet: {body_text[:1000]}")

finally:
    driver.quit()
