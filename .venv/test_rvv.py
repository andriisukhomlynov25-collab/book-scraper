import undetected_chromedriver as uc
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_rvv_kniga(driver):
    wait = WebDriverWait(driver, 10)
    
    try:
        # Шукаємо заголовок сторінки (назва книги)
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        title = title_el.text
    except Exception as e:
        print("Не вдалося знайти назву книги.")
        title = "Не знайдено"

    price = "Не знайдено"
    try:
        # rvv-kniga.com найімовірніше зроблений на WooCommerce або подібній CMS
        # Шукаємо елементи з класом price
        price_elements = driver.find_elements(By.CSS_SELECTOR, ".price, .product-price, [data-price]")
        
        # Якщо стандартні класи не знайшли, шукаємо по тексту валюти
        if not price_elements:
            price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₴') or contains(text(), 'грн') or contains(text(), 'UAH')]")
            
        for el in price_elements:
            text = el.text
            if text and any(c.isdigit() for c in text):
                # Відкидаємо довгі тексти (напр. блоки опису доставки)
                if len(text) < 40 and "доставка" not in text.lower():
                    price = text
                    break
    except:
        pass

    print("\n--- Результат парсингу rvv-kniga.com ---")
    print(f"Назва книги: {title}")
    print(f"Ціна (як текст):  {price}")
    
    if price != "Не знайдено":
        # Очищуємо ціну
        clean_price = re.sub(r'[^\d.,]', '', price).replace(',', '.')
        if clean_price.count('.') > 1:
            parts = clean_price.split('.')
            clean_price = "".join(parts[:-1]) + "." + parts[-1]
            
        if clean_price:
            print(f"Чиста ціна (float): {float(clean_price)}")
    print("-" * 30)

def test_rvv():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    print("Запускаємо браузер...")
    driver = uc.Chrome(options=options, version_main=147)
    
    url = "https://rvv-kniga.com/product/suspilni-verstvy-galyczkoyi-rusy-xiv-xv-v-rozvidka-ivana-lynnychenka-antykvarna-knyga-1899-r/?srsltid=AfmBOopfGQ_SIl8F66-4BeRbbBOr9zJHneTBzuP8fjjbNe2_X_hHIYP5"
    
    print(f"\nПереходимо на rvv-kniga.com...")
    try:
        driver.get(url)
        time.sleep(5)
        
        # Універсальне закриття кукі
        try:
            xpath_selectors = [
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'прийняти')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'akceptuj')]",
                "//button[contains(text(), 'Ok, zgadzam')]"
            ]
            for xpath in xpath_selectors:
                elements = driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        el.click()
                        time.sleep(0.5)
        except:
            pass
            
        extract_rvv_kniga(driver)
        
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_rvv()
