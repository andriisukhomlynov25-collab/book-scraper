import os
import undetected_chromedriver as uc
import time
import urllib.parse
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import DRIVER_PATH, CHROME_VERSION

def extract_olx_search_results(driver):
    wait = WebDriverWait(driver, 10)
    
    try:
        # Чекаємо появи карток товарів. На OLX вони зазвичай мають атрибут data-cy="l-card"
        cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-cy="l-card"]')))
    except:
        # Альтернативний селектор, якщо структура змінилася
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, '.css-1sw7q4x') # частий клас для карток OLX
            if not cards:
                cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="listing-grid"] > div')
        except:
            print("Не вдалося знайти картки товарів на сторінці пошуку.")
            return

    if not cards:
        print("Результатів не знайдено.")
        return

    print(f"Знайдено {len(cards)} оголошень. Аналізуємо перші кілька...\n")
    
    for idx, card in enumerate(cards[:5]): # Беремо перші 5 для тесту
        text = card.text
        if not text:
            continue
            
        lines = [line for line in text.split('\n') if line.strip()]
        if len(lines) < 2:
            continue
            
        # На OLX назва зазвичай йде серед перших рядків
        title = lines[0]
        if title.lower() in ["top", "реклама", "promowane"]:
            title = lines[1] if len(lines) > 1 else "Невідомо"
            
        # Шукаємо ціну (в злотих zł або гривнях грн)
        price = "Не знайдено"
        price_match = re.search(r'(\d+[\s\d,]*(?:zł|грн))', text)
        if price_match:
            price = price_match.group(1)
            
        print(f"--- Оголошення {idx+1} ---")
        print(f"Назва: {title}")
        print(f"Ціна:  {price}")
        
        if price != "Не знайдено":
            clean_price = re.sub(r'[^\d.,]', '', price).replace(',', '.')
            if clean_price:
                print(f"Чиста ціна (float): {float(clean_price)}")
        print("-" * 30)

def test_olx_search():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    print("Запускаємо браузер...")
    driver = uc.Chrome(options=options, version_main=CHROME_VERSION, driver_executable_path=DRIVER_PATH)
    
    long_title = "Колдовство въ Юго-Западной Руси въ XVIII ст. - Арсенія Сѣлецкаго (репрінт)"
    # Для кращого пошуку на OLX краще брати перші 4-5 слів, особливо якщо є старі символи "ъ", "ѣ"
    short_title = " ".join(long_title.split()[:5])
    
    print(f"\nПовна назва: {long_title}")
    print(f"Назва для пошуку: {short_title}")
    
    encoded_title = urllib.parse.quote(short_title)
    
    # Використовуємо olx.pl як ви просили (можна змінити на olx.ua)
    url = f"https://www.olx.pl/oferty/q-{encoded_title}/"
    # Якщо потрібно шукати на olx.ua:
    # url = f"https://www.olx.ua/uk/list/q-{encoded_title}/"
    
    print(f"Переходимо за пошуковим посиланням: {url}")
    
    try:
        driver.get(url)
        time.sleep(5) # Даємо час на завантаження сторінки
        
        # Універсальне закриття кукі та банерів
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
            
        extract_olx_search_results(driver)
        
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_olx_search()