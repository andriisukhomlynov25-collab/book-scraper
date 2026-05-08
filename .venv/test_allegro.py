import undetected_chromedriver as uc
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_allegro_results(driver, target_year):
    wait = WebDriverWait(driver, 10)
    
    try:
        # Чекаємо завантаження карток товарів
        articles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article")))
    except:
        print("Не вдалося знайти товари на сторінці.")
        return
        
    print(f"Знайдено {len(articles)} блоків на сторінці. Аналізуємо ті, що є товарами...\n")
    
    offers_found = 0
    for idx, article in enumerate(articles):
        text = article.text
        # Відсіюємо порожні блоки або ті, де немає ціни (zł)
        if not text or "zł" not in text: 
            continue
            
        lines = [line for line in text.split('\n') if line.strip()]
        if len(lines) < 2: 
            continue
            
        offers_found += 1
        
        # Назва зазвичай йде першим або другим рядком (після тегів типу Smart)
        title = lines[0]
        if "Smart!" in title or "dostawa" in title.lower():
            title = lines[1]
            
        # Шукаємо мову публікації
        lang_match = re.search(r'Język\s*(?:publikacji)?:\s*([a-zA-Z]+)', text, re.IGNORECASE)
        language = lang_match.group(1).strip().lower() if lang_match else "не вказано"
        
        # Фільтруємо: пропускаємо, якщо мова вказана і це не польська
        if language != "не вказано" and "polski" not in language:
            print(f"--- Пропозиція (Пропущено) ---")
            print(f"Назва: {title}")
            print(f"❌ Пропущено, бо мова: {language} (шукаємо лише польські)")
            print("-" * 30)
            continue

        # Шукаємо рік
        year = "Не вказано"
        year_match = re.search(r'Rok wydania:\s*(\d{4})', text)
        if year_match:
            year = year_match.group(1)
        else:
            # Шукаємо рік просто в тексті або в назві
            year_match = re.search(r'\b(18\d{2}|19\d{2}|20\d{2})\b', title)
            if year_match:
                year = f"{year_match.group(1)} (знайдено в назві)"
                
        # Шукаємо ціну
        price = "Не знайдено"
        price_match = re.search(r'(\d+[ ,]\d{2}\s*zł)', text)
        if price_match:
            price = price_match.group(1)
            
        print(f"--- Пропозиція {offers_found} ---")
        print(f"Назва: {title}")
        print(f"Рік:   {year}")
        print(f"Ціна:  {price}")
        
        # Перевіряємо, чи збігається рік з цільовим
        if str(target_year) in text:
            print(f"✅ ЗНАЙДЕНО ЦІЛЬОВИЙ РІК ({target_year})!")
        else:
            print(f"❌ Не той рік")
        print("-" * 30)

def test_allegro():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    print("Запускаємо браузер...")
    driver = uc.Chrome(options=options, version_main=147)
    
    url = "https://allegro.pl/listing?string=karol%20szajnocha%2C%20dwa%20lata&srsltid=AfmBOoofsCzTy5hB6A4RNWTexO0tny40WiCOK-Btlh4IzGREVXVLWIen"
    target_year = "1877" # З вашої таблиці (рядок 4)
    
    print(f"\nПереходимо на Allegro...")
    try:
        driver.get(url)
        time.sleep(4)
        
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
            
            # Для Allegro часто використовується data-role
            allegro_btn = driver.find_elements(By.CSS_SELECTOR, "button[data-role='accept-consent']")
            if allegro_btn and allegro_btn[0].is_displayed():
                allegro_btn[0].click()
        except:
            pass
            
        print(f"\nШукаємо книгу 1877 року...\n")
        extract_allegro_results(driver, target_year)
        
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_allegro()
