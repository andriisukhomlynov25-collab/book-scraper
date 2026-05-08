import undetected_chromedriver as uc
import time
import urllib.parse
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_price(driver):
    page_source = driver.page_source
    if "We were unable to find exact matches" in page_source:
        print("STATUS: No exact matches found (Suggestions are shown).")
        return None

    wait = WebDriverWait(driver, 10)
    selectors = [
        "p[data-test-id='item-price']",
        "p.item-price",
        "[id^='item-price-']",
        "#book-price",
        ".item-price"
    ]
    
    price_text = None
    for sel in selectors:
        try:
            element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, sel)))
            price_text = element.get_attribute("innerText") or element.text
            if price_text and any(c.isdigit() for c in price_text):
                print(f"Target found via selector: {sel}")
                break
        except:
            continue
            
    if price_text:
        print(f"Raw price string found: '{price_text}'")
        if '-' in price_text:
            price_text = price_text.split('-')[0]
        elif ' to ' in price_text.lower():
            price_text = price_text.lower().split(' to ')[0]
            
        clean_price = re.sub(r'[^\d.,]', '', price_text).replace(',', '.')
        if clean_price.count('.') > 1:
            parts = clean_price.split('.')
            clean_price = "".join(parts[:-1]) + "." + parts[-1]
        
        if clean_price:
            return float(clean_price)
    return None

def test_abebooks():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    print("Starting Chrome...")
    driver = uc.Chrome(options=options, version_main=147)
    
    # Використовуємо проблемну довгу назву з вашого скріншоту
    long_title = "Soldier's Manual of Common Tasks Warrior Leader Skills Level 2, 3, 4, STP 21-24-SMCT Headquarters Department of the Army Washington DC United States Government US Army 2008 464 p"
    
    # Обрізаємо до 5 слів, як ми зробили в основному скрипті
    short_title = " ".join(long_title.split()[:5]).strip(",.() ")
    
    print(f"\nOriginal long title: {long_title}")
    print(f"Shortened title for search: {short_title}")
    
    encoded_title = urllib.parse.quote(short_title)
    url = f"https://www.abebooks.com/servlet/SearchResults?sts=t&tn={encoded_title}"
    
    print(f"\nVisiting AbeBooks URL: {url}")
    
    try:
        driver.get(url)
        time.sleep(4)
        
        price = get_price(driver)
        if price:
            print(f"\n✅ SUCCESS! Extracted valid price: ${price}")
        else:
            print("\n❌ FAILED to find price or exact match.")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    test_abebooks()
