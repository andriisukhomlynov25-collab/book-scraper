import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Add the main project dir to python path to import functions
sys.path.append("/Users/getapp/PycharmProjects/book_scraper/.venv")
from stealth_scraper_ai import find_all_price_elements, parse_price, init_driver

driver = init_driver(instance_id=99, headless=False)
try:
    url = "https://fama.ua/uk/p/kniga-oruel-g-kolhosp-tvaryn-myunkhen-vyd-vo-prometey-1947-ukrayinskoyu-movoyu-28138"
    print(f"Navigating to {url}")
    driver.get(url)
    time.sleep(5)
    
    # Get page title
    print(f"Page Title: {driver.title}")
    
    # Try finding price candidates
    candidates = find_all_price_elements(driver)
    print("\n--- Price Candidates Found ---")
    for cand in candidates:
        print(f"Text: '{cand['price_display']}' | Val: {cand['value']} | Curr: {cand['currency']}")
        
    # Save screenshot
    screenshot_path = "/Users/getapp/PycharmProjects/book_scraper/scratch/fama_test.png"
    driver.save_screenshot(screenshot_path)
    print(f"\nScreenshot saved to {screenshot_path}")
    
    # Now let's try Violity
    url2 = "https://violity.com/ua/119317233-kolgosp-tvarin-oruel-diaspora-1947-rik"
    print(f"\nNavigating to {url2}")
    driver.get(url2)
    time.sleep(5)
    
    print(f"Page Title: {driver.title}")
    candidates2 = find_all_price_elements(driver)
    print("\n--- Price Candidates Found on Violity ---")
    for cand in candidates2:
        print(f"Text: '{cand['price_display']}' | Val: {cand['value']} | Curr: {cand['currency']}")
        
    screenshot_path2 = "/Users/getapp/PycharmProjects/book_scraper/scratch/violity_test.png"
    driver.save_screenshot(screenshot_path2)
    print(f"Screenshot saved to {screenshot_path2}")

finally:
    driver.quit()
