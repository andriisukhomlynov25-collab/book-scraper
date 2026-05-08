import os
import undetected_chromedriver as uc
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_bam(driver):
    wait = WebDriverWait(driver, 10)
    
    # Шукаємо назву книги (зазвичай h1)
    try:
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        title = title_el.text
    except Exception as e:
        print("Не вдалося знайти назву книги. Можливо, спрацював захист Cloudflare/Akamai.")
        title = "Не знайдено"

    price = "Не знайдено"
    try:
        # Для Books-A-Million шукаємо ціну по всьому тексту сторінки для надійності
        # (часто буває "Online Price $32.95" або подібне)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Якщо в тексті є типові фрази Cloudflare (англійською чи російською/українською), сайт заблокував бот
        cloudflare_phrases = ["Access Denied", "Checking your browser", "проверки безопасности", "перевірки безпеки", "сервис безопасности", "Cloudflare"]
        for phrase in cloudflare_phrases:
            if phrase.lower() in page_text.lower():
                print("STATUS: ⚠️ ВИЯВЛЕНО БЛОКУВАННЯ CLOUDFLARE! Сайт перевіряє, чи ми бот.")
                break
            
        # Шукаємо першу ціну формату $XX.XX
        match = re.search(r'\$(\d+[.,]\d{2})', page_text)
        if match:
            price = match.group(0)
    except:
        pass

    print("\n--- Результат парсингу booksamillion.com ---")
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

import random

from config import DRIVER_PATH, CHROME_VERSION

def simulate_human(driver):
    # Імітація людського гортання сторінки
    try:
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        if total_height > 1000:
            for _ in range(3):
                scroll_to = random.randint(200, total_height // 2)
                driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                time.sleep(random.uniform(0.5, 2.0))
            driver.execute_script("window.scrollTo(0, 0);")
    except:
        pass

def test_bam():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    # Додатковий захист від виявлення
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("Запускаємо браузер...")
    driver = uc.Chrome(options=options, version_main=CHROME_VERSION, driver_executable_path=DRIVER_PATH)
    
    url = "https://www.booksamillion.com/p/Pen-Ink-Drawing/George-Hartnell-Bartlett/9781016901239"
    
    try:
        print("\n⏳ ПРОГРІВ: Переходимо спочатку на головну сторінку booksamillion.com...")
        driver.get("https://www.booksamillion.com/")
        
        # Імітуємо присутність живої людини на головній сторінці протягом 12 секунд
        for i in range(12):
            time.sleep(1)
            if i % 3 == 0:
                driver.execute_script(f"window.scrollBy(0, {random.randint(150, 400)});")
                
        print("✅ Прогрів завершено. Переходимо на сторінку книги...")
        driver.get(url)
        
        # Даємо час Cloudflare подумати і знову гортаємо сторінку
        time.sleep(5)
        simulate_human(driver)
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
            
        extract_bam(driver)
        
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_bam()