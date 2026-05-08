import undetected_chromedriver as uc
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random

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

def extract_harvard_details(driver):
    wait = WebDriverWait(driver, 10)
    
    details = {
        "price": None,
        "currency": "£"
    }
    
    try:
        # Селектори для ціни на Harvard University Press
        # Згідно з вашим скріншотом, використовуємо атрибут data-purchase-btnprice або клас .ml-4 всередині кнопки
        price_selectors = [
            "span[data-purchase-btnprice]",
            ".ml-4[data-purchase-btnprice]",
            "button[data-component='products:product-purchase'] .ml-4"
        ]
        
        for sel in price_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, sel)
                text = element.get_attribute("innerText") or element.text
                if text and any(c.isdigit() for c in text):
                    # На сайті Гарварду може бути кілька цін (фунти та євро через крапку)
                    # Наприклад: "£39.95 • 41,95 €"
                    # Беремо першу частину
                    if "•" in text:
                        text = text.split("•")[0]
                    
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

def test_harvard():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("Запускаємо Chrome для Harvard University Press...")
    driver = uc.Chrome(options=options, version_main=147)
    
    book_title = "Theda Skocpol — Protecting Soldiers and Mothers: The Political Origins of Social Policy in the United States"
    direct_url = "https://www.hup.harvard.edu/books/9780674717664"
    
    print(f"\nТестуємо книгу: {book_title}")
    print(f"URL: {direct_url}")
    
    try:
        driver.get(direct_url)
        time.sleep(5)
        simulate_human_interaction(driver)
        
        results = extract_harvard_details(driver)
        
        if results["price"]:
            print(f"\n✅ УСПІХ!")
            print(f"Ціна книги: {results['currency']}{results['price']}")
        else:
            print("\n❌ НЕ ВДАЛОСЯ знайти ціну.")

    except Exception as e:
        print(f"Виникла помилка: {e}")
    finally:
        print("\nЗакриваємо браузер...")
        driver.quit()

if __name__ == "__main__":
    test_harvard()
