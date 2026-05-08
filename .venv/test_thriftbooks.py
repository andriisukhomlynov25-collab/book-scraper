import undetected_chromedriver as uc
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_thriftbooks(driver):
    wait = WebDriverWait(driver, 10)
    
    try:
        # Шукаємо назву (h1)
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        title = title_el.text
    except Exception as e:
        print("Не вдалося знайти назву книги.")
        title = "Не знайдено"

    price = "Не знайдено"
    try:
        # Найбільш надійний спосіб для ThriftBooks - парсити текст всієї сторінки, оскільки класи дуже динамічні
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Шукаємо ціну формату $XX.XX. 
        # ThriftBooks часто пише щось на кшталт "Hardcover $32.95" або "New $32.95"
        match = re.search(r'\$(\d+[.,]\d{2})', page_text)
        if match:
            price = match.group(0)
    except:
        pass

    print("\n--- Результат парсингу thriftbooks.com ---")
    print(f"Назва книги: {title}")
    print(f"Ціна (як текст):  {price}")
    
    if price != "Не знайдено":
        # Якщо в ціні є "From $4.99" або діапазон, залишаємо перше знайдено число
        if '-' in price:
            price = price.split('-')[0]
        elif ' to ' in price.lower():
            price = price.lower().split(' to ')[0]
            
        clean_price = re.sub(r'[^\d.,]', '', price).replace(',', '.')
        if clean_price.count('.') > 1:
            parts = clean_price.split('.')
            clean_price = "".join(parts[:-1]) + "." + parts[-1]
            
        if clean_price:
            print(f"Чиста ціна (float): {float(clean_price)}")
    print("-" * 30)

def test_thriftbooks():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    print("Запускаємо браузер...")
    driver = uc.Chrome(options=options, version_main=147)
    
    url = "https://www.thriftbooks.com/w/pen-and-ink-drawing-a-series-of-drawings-showing-its-perfect-adaptability-to-the-modern-processes-of-reproduction_george-hartnell-bartlett/20661764/?srsltid=AfmBOoq7O4h6fYMDjchfOlpG-iK5Y3Q25QUNrX3xPs0KBgD-xre4KPqd#edition=68402468&idiq=59708386"
    
    print(f"\nПереходимо на thriftbooks.com...")
    try:
        driver.get(url)
        time.sleep(5)
        
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
            
        extract_thriftbooks(driver)
        
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_thriftbooks()
