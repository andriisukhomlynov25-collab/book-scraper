import undetected_chromedriver as uc
import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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

def extract_elefant_details(driver):
    wait = WebDriverWait(driver, 10)
    details = {"price": None, "currency": "lei"}
    
    try:
        # Селектори для elefant.ro
        # Згідно з вашим скріншотом, використовуємо клас .current-price
        price_selectors = [
            ".current-price",
            ".price-block .current-price",
            "span[class*='current-price']"
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
        print(f"Помилка при парсингу ціни Elefant: {e}")
    return details

def test_elefant():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("Запускаємо Chrome для Elefant.ro...")
    driver = uc.Chrome(options=options, version_main=147)
    
    book_title = "Plokhy S. Cernobîl: Istoria unei catastrofe nucleare / Editura Trei. București"
    direct_url = "https://www.elefant.ro/cernobil-istoria-unei-catastrofe-nucleare_48326507-65fb-43af-ac08-cacc0045bf42"
    
    print(f"\nТестуємо книгу: {book_title}")
    
    try:
        driver.get(direct_url)
        time.sleep(5)
        simulate_human_interaction(driver)
        
        # Спроба закрити банери (на скріншоті видно великий синій банер з хрестиком)
        try:
            # Селектор для хрестика на банері elefant
            close_btn = driver.find_elements(By.CSS_SELECTOR, "div.close-button, .close-modal, .ic-close")
            for btn in close_btn:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
        except:
            pass

        results = extract_elefant_details(driver)
        
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
    test_elefant()
