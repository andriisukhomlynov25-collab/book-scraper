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

def extract_piramida_details(driver):
    wait = WebDriverWait(driver, 10)
    details = {"price": None, "currency": "грн"}
    
    try:
        # Селектори для Piramida Books
        # Згідно з вашим скріншотом, використовуємо клас .fm-module-price-new
        price_selectors = [
            ".fm-module-price-new",
            ".fm-price-block span",
            ".fm-product-right .fm-module-price-new"
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
        print(f"Помилка при парсингу ціни Piramida: {e}")
    return details

def test_piramida():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("Запускаємо Chrome для Piramida Books...")
    driver = uc.Chrome(options=options, version_main=147)
    
    book_title = "Дашкевич Я. Постаті: Нариси про діячів історії, політики, культури. — Львів, 2006."
    direct_url = "https://piramidabooks.net/vsi-knyzhky/postati-narysy-pro-diyachiv-istoriyi-polityky-kultury"
    
    print(f"\nТестуємо книгу: {book_title}")
    
    try:
        driver.get(direct_url)
        time.sleep(5)
        simulate_human_interaction(driver)
        
        # Використовуємо універсальну функцію закриття поп-апів, яку ми додали в основний код
        # (в тесті просто імітуємо її частину)
        try:
            close_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Close') or contains(text(), 'Прийняти')]")
            for btn in close_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
        except:
            pass

        results = extract_piramida_details(driver)
        
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
    test_piramida()
