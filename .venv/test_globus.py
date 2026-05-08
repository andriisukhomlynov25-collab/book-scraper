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

def extract_globus_details(driver):
    wait = WebDriverWait(driver, 10)
    
    details = {
        "price": None,
        "currency": "$"
    }
    
    try:
        # Селектори для ціни книги на Globus Books
        # Згідно з вашим скріншотом, використовуємо клас .BL_pr2 або itemprop='price'
        price_selectors = [
            ".BL_pr2",
            "span[itemprop='price']",
            ".bookdetail-price .BL_pr2",
            ".price .BL_pr2"
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

def test_globus():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("Запускаємо Chrome для Globus Books...")
    driver = uc.Chrome(options=options, version_main=147)
    
    book_title = "Л. Перепелкіна — Екуменізм: путь, ведущий в погибель"
    direct_url = "https://www.globusbooks.com/pages/books/24896/l-perepelkina/ekumenizm-put-veduschij-k-pogibeli"
    
    print(f"\nТестуємо книгу: {book_title}")
    print(f"URL: {direct_url}")
    
    try:
        driver.get(direct_url)
        time.sleep(5)
        simulate_human_interaction(driver)
        
        # Спроба прийняти кукі, якщо з'являться
        try:
            cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'OK') or contains(text(), 'Agree')]")
            for btn in cookie_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
        except:
            pass

        results = extract_globus_details(driver)
        
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
    test_globus()
