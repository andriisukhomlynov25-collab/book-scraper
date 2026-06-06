import os
import sys
import time

sys.path.append("/Users/getapp/PycharmProjects/book_scraper/.venv")
from stealth_scraper_ai import init_driver

driver = init_driver(instance_id=98, headless=False)
try:
    url = "https://www.olx.ua/d/uk/obyavlenie/kniga-1984-kolgosp-tvarin-dzhordzh-orvell-ksd-IDZ3ZvW.html"
    print(f"Navigating to {url}")
    driver.get(url)
    time.sleep(8)
    
    title = driver.title
    print(f"Loaded Page Title: {title}")
    
    page_source = driver.page_source
    print(f"Page Source length: {len(page_source)} chars")
    
    # Save page source to scratch/olx_source.html
    os.makedirs("/Users/getapp/PycharmProjects/book_scraper/scratch", exist_ok=True)
    with open("/Users/getapp/PycharmProjects/book_scraper/scratch/olx_source.html", "w", encoding="utf-8") as f:
        f.write(page_source)
    print("Saved page source to scratch/olx_source.html")
    
    # Save screenshot
    screenshot_path = "/Users/getapp/PycharmProjects/book_scraper/scratch/olx_test.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    # Check if there are elements with price
    # Typical OLX class for price is css-12vvo3gg or card-price or similar
    price_elements = driver.find_elements(By.CSS_SELECTOR, "h3") if 'By' in globals() else driver.find_elements("css selector", "h3")
    print(f"Found {len(price_elements)} h3 elements")
    for el in price_elements[:5]:
        print(f"h3 text: '{el.text}'")

finally:
    driver.quit()
