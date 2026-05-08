import os
import undetected_chromedriver as uc
import time
import urllib.parse
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random

from config import DRIVER_PATH, CHROME_VERSION

def simulate_human_interaction(driver):
    try:
        actions = ActionChains(driver)
        for _ in range(random.randint(2, 5)):
            x = random.randint(-50, 50)
            y = random.randint(-50, 50)
            try:
                actions.move_by_offset(x, y).perform()
                time.sleep(random.uniform(0.1, 0.2))
            except:
                actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
    except:
        pass

def extract_biblio_details(driver):
    wait = WebDriverWait(driver, 10)
    
    details = {
        "price": None,
        "currency": "$"
    }
    
    try:
        # Селектори для ціни книги
        price_selectors = [
            ".the-price",
            ".book-buy-price .the-price",
            "span[itemprop='price']",
            ".price"
        ]
        
        for sel in price_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, sel)
                text = element.get_attribute("innerText") or element.text
                if text and any(c.isdigit() for c in text):
                    # Очищення ціни
                    clean_price = re.sub(r'[^\d.,]', '', text).replace(',', '.')
                    details["price"] = float(clean_price)
                    print(f"Знайдено ціну через {sel}: {details['price']}")
                    break
            except:
                continue
                
    except Exception as e:
        print(f"Помилка при парсингу ціни: {e}")
        
    return details

def test_biblio():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("Запускаємо Chrome для Biblio...")
    driver = uc.Chrome(options=options, version_main=CHROME_VERSION, driver_executable_path=DRIVER_PATH)
    
    book_title = "Gogol, Nikolai. The Overcoat and Other Short Stories. — New York : Dover Publications, Inc., 1992. — 112 p."
    direct_url = "https://www.biblio.com/book/overcoat-other-short-stories-gogol-nikolai/d/120340272?srsltid=AfmBOooijsgLiGLboB5Ck28RYGX7XVjFiNNs8HDbHroUhgetbiW76zMa"
    
    print(f"\nТестуємо книгу: {book_title}")
    print(f"URL: {direct_url}")
    
    try:
        driver.get(direct_url)
        time.sleep(5)
        simulate_human_interaction(driver)
        
        results = extract_biblio_details(driver)
        
        if results["price"]:
            print(f"\n✅ УСПІХ!")
            print(f"Ціна книги (без доставки): {results['currency']}{results['price']}")
        else:
            print("\n❌ НЕ ВДАЛОСЯ знайти ціну.")

    except Exception as e:
        print(f"Виникла помилка: {e}")
    finally:
        print("\nЗакриваємо браузер...")
        driver.quit()


if __name__ == "__main__":
    test_biblio()