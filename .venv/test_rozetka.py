import os
import undetected_chromedriver as uc
import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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

def extract_rozetka_details(driver):
    wait = WebDriverWait(driver, 10)
    details = {"price": None, "currency": "грн"}
    
    try:
        # Селектори для Rozetka
        # Згідно з вашим скріншотом, використовуємо клас .product-price__big
        price_selectors = [
            ".product-price__big",
            "p.product-price__big",
            ".product-prices__big",
            ".product-about__price-wrapper .product-price__big"
        ]
        
        for sel in price_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, sel)
                text = element.get_attribute("innerText") or element.text
                if text and any(c.isdigit() for c in text):
                    # Очищення ціни
                    clean_price = re.sub(r'[^\d.,]', '', text).replace(',', '.')
                    # На Розетці часто є пробіл між тисячами (напр. 1 580)
                    clean_price = clean_price.replace(' ', '').replace('\xa0', '')
                    details["price"] = float(clean_price)
                    print(f"Знайдено ціну через {sel}: {details['price']}")
                    break
            except:
                continue
    except Exception as e:
        print(f"Помилка при парсингу ціни Rozetka: {e}")
    return details

def test_rozetka():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("Запускаємо Chrome для Rozetka.com.ua...")
    driver = uc.Chrome(options=options, version_main=CHROME_VERSION, driver_executable_path=DRIVER_PATH)
    
    book_title = "Щупак І. Я. Всесвітня історія (рівень стандарту)"
    direct_url = "https://rozetka.com.ua/ua/402850905/p402850905/"
    
    print(f"\nТестуємо книгу: {book_title}")
    
    try:
        driver.get(direct_url)
        time.sleep(5)
        simulate_human_interaction(driver)
        
        # Закриваємо поп-апи Розетки
        try:
            # На Розетці часто бувають банери та вибір міста
            close_btn = driver.find_elements(By.CSS_SELECTOR, "button.modal__close, .city-selection__close")
            for btn in close_btn:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
        except:
            pass

        results = extract_rozetka_details(driver)
        
        if results["price"]:
            print(f"\n✅ УСПІХ!")
            print(f"Ціна книги: {results['price']} {results['currency']}")
        else:
            print("\n❌ НЕ ВДАЛОСЯ знайти ціну.")

    except Exception as e:
        print(f"Виникла помилка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_rozetka()