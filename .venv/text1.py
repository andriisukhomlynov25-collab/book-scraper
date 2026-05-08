import os
import re
import time
import random
import requests
import json
import urllib.parse
import gspread
import undetected_chromedriver as uc
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# ================= НАЛАШТУВАННЯ =================
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = '1F1KctUExEnsh9uZpLxcID6HgY1gxkv5fiuvXGMOYw5s'
SHARED_DRIVE_FOLDER_ID = '0AHvgRKQpv3qrUk9PVA'
# =================================================
# Додайте сюди ваші ключі Serper API. Скрипт автоматично перемикатиметься, якщо кредити закінчаться.
SERPER_API_KEYS = [
    '18a31827f8487bd89b2303ca8dea91faddeace0c',
    # 'ВАШ_ДРУГИЙ_КЛЮЧ',
]
current_key_index = 0
# =================================================

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
sheet_client = gspread.authorize(creds)
drive_service = build('drive', 'v3', credentials=creds)
spreadsheet = sheet_client.open_by_key(SPREADSHEET_ID)

def log_message(message):
    # Отримуємо поточний час у форматі Години:Хвилини:Секунди
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] {message}")

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    
    driver = uc.Chrome(options=options, version_main=147)
    return driver

def simulate_human_interaction(driver):
    """Імітація рухів мишкою та випадкових пауз"""
    try:
        actions = ActionChains(driver)
        # Випадкові рухи мишкою
        for _ in range(random.randint(2, 5)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            try:
                actions.move_by_offset(x_offset, y_offset).perform()
                time.sleep(random.uniform(0.1, 0.3))
            except:
                # Якщо мишка виходить за межі екрану, скидаємо в центр
                actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
    except Exception as e:
        pass


def set_amazon_location(driver):
    try:
        driver.get("https://www.amazon.com/")
        time.sleep(random.uniform(3, 5))
        
        # Перевіряємо, чи є кнопка зміни локації
        try:
            # Закриваємо початковий поп-ап "Deliver to Ukraine", якщо він є
            dismiss_btn = driver.find_elements(By.CSS_SELECTOR, "input[data-action-type='DISMISS']")
            if dismiss_btn:
                dismiss_btn[0].click()
                time.sleep(1)
        except:
            pass

        wait = WebDriverWait(driver, 10)
        location_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link")))
        location_btn.click()
        time.sleep(2)
        
        zip_in = wait.until(EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput")))
        zip_in.send_keys("10001")
        
        driver.find_element(By.ID, "GLUXZipUpdate").click()
        time.sleep(2)
        
        # Натискаємо "Done" або "Continue"
        try:
            driver.find_element(By.NAME, "glowDoneButton").click()
        except:
            driver.refresh()
            
        time.sleep(3)
        log_message("🌍 Локація встановлена: USA (10001)")
    except Exception as e:
        log_message(f"⚠️ Не вдалося змінити локацію: {e}")

def get_serper_data(query):
    global current_key_index
    
    while current_key_index < len(SERPER_API_KEYS):
        api_key = SERPER_API_KEYS[current_key_index]
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
                json={"q": query}
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Якщо 403 або 401 — швидше за все, закінчилися кредити або ключ невірний
            if response.status_code in [401, 403]:
                log_message(f"⚠️ Ключ №{current_key_index + 1} вичерпано або невалідний. Перемикаюсь...")
                current_key_index += 1
                continue
            else:
                log_message(f"❌ Помилка Serper (Status {response.status_code}): {response.text}")
                return None
        except Exception as e:
            log_message(f"⚠️ Помилка мережі Serper: {e}")
            return None
            
    log_message("🚨 УСІ Serper API ключі вичерпано!")
    return None

def close_popups(driver):
    """Універсальна функція для агресивного закриття кукі, банерів та поп-апів"""
    css_selectors = [
        "button[aria-label='Close']",
        ".main-pwa-close-button",
        "#sp-cc-accept",           # Amazon
        ".pm-close-button",
        "button.cm-banner__close",
        "a[data-test='close-guest-modal']",
        ".modal-close",
        ".ui-btn-close",            # Yakaboo
        ".language-button",         # Yakaboo
        "button[data-role='accept-consent']", # Allegro
        "#gdpr-banner-accept",      # eBay
        ".close-button",
        ".close-modal",
        ".modal__close",
        ".newsletter-popup-close",
        "button.close",
        ".ic-close"
    ]
    
    xpath_selectors = [
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'прийняти')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'akceptuj')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'allow')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'zgadzam')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'acceptă')]", # Romanian
        "//button[contains(text(), 'OK')]",
        "//button[contains(text(), 'Ok')]",
        "//span[contains(text(), 'Close')]",
        "//span[contains(text(), 'Закрити')]",
        "//*[contains(@class, 'close') and contains(@class, 'button')]",
        "//*[contains(@id, 'cookie') or contains(@class, 'cookie')]//button"
    ]

    # Робимо два проходи, бо закриття одного вікна може активувати інше
    for _ in range(2):
        for selector in css_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed():
                        # Використовуємо JS для надійного кліку (якщо кнопка перекрита)
                        driver.execute_script("arguments[0].click();", el)
                        log_message(f"   🧹 Закрито банер (CSS): {selector}")
                        time.sleep(0.5)
            except:
                pass

        for xpath in xpath_selectors:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        driver.execute_script("arguments[0].click();", el)
                        log_message(f"   🧹 Закрито банер (XPath)")
                        time.sleep(0.5)
            except:
                pass

def select_paper_format(driver):
    """Універсальна функція для вибору паперового формату книги (Paperback, Hardcover, Twarda/Miękka okładka)"""
    # XPaths для кнопок вибору формату різними мовами
    paper_xpaths = [
        "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'paperback')]",
        "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'hardcover')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'paperback')]",
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'hardcover')]",
        "//li[contains(@class, 'swatchElement') and contains(@class, 'paperback')]//a",
        "//li[contains(@class, 'swatchElement') and contains(@class, 'hardcover')]//a",
        "//a[contains(text(), 'Twarda okładka')]",
        "//a[contains(text(), 'Miękka okładka')]",
        "//button[contains(text(), 'Twarda')]",
        "//button[contains(text(), 'Miękka')]"
    ]
    
    # Спочатку спробуємо знайти Paperback, якщо немає - Hardcover
    format_selected = False
    for xpath in paper_xpaths:
        if format_selected:
            break
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    el.click()
                    log_message("   📖 Обрано паперовий формат книги.")
                    time.sleep(1.5)
                    format_selected = True
                    break
        except:
            pass

def get_product_price(driver):
    """Універсальна функція для зчитування ціни (Amazon, eBay, AbeBooks)"""
    try:
        # ЗАВЖДИ спершу обираємо паперовий формат, якщо на сторінці є такий вибір
        select_paper_format(driver)
        
        page_source = driver.page_source
        if "Access Denied" in page_source or "Checking your browser" in page_source:
            log_message("   🛡️ Виявлено блок (Access Denied / Cloudflare). Пропуск...")
            return None

        # Посилена перевірка на сторінку "No results" або "Рекомендації"
        no_results_msgs = [
            "We were unable to find exact matches", 
            "0 results for", 
            "No results found", 
            "Closest match to your search",
            "Try again, but check your spelling",
            "No matching results were found"
        ]
        if any(msg in page_source for msg in no_results_msgs):
            return None

        # Очікуємо базового завантаження сторінки один раз
        wait = WebDriverWait(driver, 5)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            pass
        
        # Список селекторів для різних сайтів
        selectors = [
            # Amazon (пріоритетні для книг)
            "#tmm-grid-swatch-PAPERBACK .slot-price",
            "#tmm-grid-swatch-KINDLE .slot-price",
            ".swatchElement.selected .a-color-price", 
            ".a-button-selected .a-color-price",
            ".slot-price",
            "#kindle-price",
            "#price",
            ".a-price .a-offscreen",
            "#corePrice_feature_div .a-offscreen", 
            ".a-price-whole", 
            
            # eBay
            ".x-price-primary .ux-textspans", 
            ".x-bin-price .ux-textspans",
            "div[data-testid='x-price-primary']",
            ".x-price-primary",
            
            # AbeBooks
            "p[data-test-id='item-price']",
            "p.item-price",
            "[id^='item-price-']",
            "#book-price",
            ".item-price",
            
            # Biblio
            ".the-price",
            ".book-buy-price .the-price",
            
            # Globus Books
            ".BL_pr2",
            "span[itemprop='price']",
            
            # Harvard University Press
            "span[data-purchase-btnprice]",
            ".ml-4[data-purchase-btnprice]",
            
            # Yakaboo (основна ціна на сторінці товару)
            ".product-sidebar__price .price__value",
            ".price__value",
            
            # Piramida Books
            ".fm-module-price-new",
            ".fm-price-block span",
            
            # Elefant.ro
            ".current-price",
            ".price-block .current-price",
            
            # Rozetka
            ".product-price__big",
            "p.product-price__big",
            
            # Books-A-Million
            ".our-price",
            ".price-display",
            
            # General fallbacks
            ".price",
            ".current-price",
            "[class*='price']"
        ]
        
        price_text = None
        
        # Спеціальна логіка для сайтів, де ціна краще шукається через текст або regex
        if "allegro.pl" in driver.current_url:
            text = driver.find_element(By.TAG_NAME, "body").text
            price_match = re.search(r'(\d+[\s,]\d{2}\s*zł)', text)
            if price_match:
                price_text = price_match.group(1)
        
        elif "thriftbooks.com" in driver.current_url:
            text = driver.find_element(By.TAG_NAME, "body").text
            price_match = re.search(r'\$(\d+[.,]\d{2})', text)
            if price_match:
                price_text = price_match.group(1)

        elif "olx." in driver.current_url:
            text = driver.find_element(By.TAG_NAME, "body").text
            price_match = re.search(r'(\d+[\s\d,]*(?:zł|грн))', text)
            if price_match:
                price_text = price_match.group(1)

        # Якщо спеціальна логіка не спрацювала, перевіряємо селектори миттєво
        if not price_text:
            for sel in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, sel)
                    for element in elements:
                        if element.is_displayed():
                            text = element.get_attribute("innerText") or element.text
                            if text and any(c.isdigit() for c in text):
                                # Для Гарварду беремо першу ціну
                                if "hup.harvard.edu" in driver.current_url and "•" in text:
                                    text = text.split("•")[0]
                                
                                price_text = text
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
                                time.sleep(0.5)
                                break
                    if price_text: break
                except:
                    continue
        
        if price_text:
            # Очищення від валютних знаків та іншого тексту
            # Якщо ціна вказана як діапазон (напр. "$5.98 - $12.00"), беремо лише першу ціну
            if '-' in price_text:
                price_text = price_text.split('-')[0]
            elif ' to ' in price_text.lower():
                price_text = price_text.lower().split(' to ')[0]
                
            # Очищення від "US $", "£", літер тощо
            clean_price = re.sub(r'[^\d.,]', '', price_text).replace(',', '.')
            # Видаляємо зайві крапки (якщо це були роздільники тисяч, напр. 1.995.00 -> 1995.00)
            if clean_price.count('.') > 1:
                parts = clean_price.split('.')
                clean_price = "".join(parts[:-1]) + "." + parts[-1]
            
            if clean_price:
                return float(clean_price)
            
    except Exception as e:
        pass
    
    return None

def visit_neutral_site(driver):
    """Заходить на випадковий популярний сайт для 'прогріву'"""
    neutral_sites = [
        "https://www.wikipedia.org/",
        "https://www.bbc.com/",
        "https://www.nytimes.com/",
        "https://www.reddit.com/"
    ]
    site = random.choice(neutral_sites)
    try:
        log_message(f"🕵️ Ротація: імітуємо перегляд {site}")
        driver.get(site)
        time.sleep(random.uniform(3, 7))
        driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
    except:
        pass


def process_books():
    driver = init_driver()
    set_amazon_location(driver)
    
    # Використовуємо першу вкладку (або можна змінити на конкретну назву)
    worksheet = spreadsheet.sheet1
    log_message(f"📑 Обробка вкладки: '{worksheet.title}'")
    ebay_warmed_up = False
    
    records = worksheet.get_all_values()[1:]
    columns_map = {0: 'F', 1: 'G', 2: 'H'}

    for i, row in enumerate(records, start=2):
        if len(row) < 3 or not row[2]: continue

        # --- ЛОГІКА ПРОДОВЖЕННЯ (ВИМКНЕНО ЗА ЗАПИТОМ) ---
        # if len(row) >= 9 and row[8].strip():
        #     continue

        # --- ПЕРЕВІРКА ТА ВІДНОВЛЕННЯ ДРАЙВЕРА ---
        try:
            _ = driver.window_handles # Надійніша перевірка сесії
        except:
            log_message("🔄 Сесія втрачена. Перезапуск браузера...")
            try: driver.quit()
            except: pass
            driver = init_driver()
            set_amazon_location(driver)
            ebay_warmed_up = False

        book_title = row[2]
        log_message(f"📘 Рядок {i}: {book_title[:40]}...")

        # --- ПОШУК З РОЗШИРЕНИМ ПЕРЕЛІКОМ САЙТІВ ---
        try:
            sites = [
                "amazon.com", "ebay.com", "abebooks.com", 
                "biblio.com", "globusbooks.com", "hup.harvard.edu",
                "allegro.pl", "booksamillion.com", "thriftbooks.com",
                "yakaboo.ua", "piramidabooks.net", "elefant.ro", "rozetka.com.ua"
            ]
            site_query = " OR ".join([f"site:{s}" for s in sites])
            search_query = f"{book_title} price ({site_query})"
            
            res = get_serper_data(search_query)
            if not res:
                all_items = []
            else:
                all_items = res.get('organic', [])
            
            links = []
            seen_domains = set()
            
            # Фільтруємо посилання, щоб переходити ТІЛЬКИ на ваші сайти
            allowed_base_domains = [s.split('.')[0] for s in sites]
            
            for item in all_items:
                link = item['link']
                domain = urllib.parse.urlparse(link).netloc.lower()
                
                # Перевірка чи домен є у списку дозволених
                is_allowed = any(base in domain for base in allowed_base_domains)
                
                if is_allowed and domain not in seen_domains:
                    # Якщо це AbeBooks з кирилицею від Serper - ігноруємо, ми зробимо своє чисте посилання
                    if "abebooks.com" in domain and any(ord(c) > 127 for c in link):
                        continue
                    links.append(link)
                    seen_domains.add(domain)
                if len(links) >= 3: break
            
            if "abebooks.com" not in seen_domains:
            if "abebooks.com" not in seen_domains:
                # Пряме посилання на сторінку пошуку (будемо вводити назву вручну через Selenium)
                links.append("https://www.abebooks.com/servlet/SearchEntry")
            
        except Exception as e:
            log_message(f"   ⚠️ Помилка Serper: {e}")
            links = []

        if not links: continue

        prices_found = []
        row_updates = []
        
        for idx, link in enumerate(links):
            try:
                if "ebay.com" in link and not ebay_warmed_up:
                    log_message("   🛡️ Прогрів eBay...")
                    driver.get("https://www.ebay.com/")
                    time.sleep(random.uniform(2, 4))
                    ebay_warmed_up = True

                log_message(f"🔗 Перехід: {link[:50]}...")
                driver.get(link)
            
            # СПЕЦІАЛЬНА ЛОГІКА ДЛЯ ABEBOOKS (КИРИЛИЦЯ)
            if "abebooks.com/servlet/SearchEntry" in link:
                try:
                    wait.until(EC.presence_of_element_located((By.NAME, "tn")))
                    title_field = driver.find_element(By.NAME, "tn")
                    title_field.clear()
                    # Чистимо назву для пошуку
                    clean_t = re.sub(r'[^a-zA-Zа-яА-ЯёЁєЄіІїЇґҐ0-9\s]', ' ', book_title)
                    short_t = " ".join(clean_t.split()[:6]).strip()
                    title_field.send_keys(short_t)
                    
                    # Шукаємо кнопку пошуку (зазвичай це input або button з типом submit)
                    try:
                        search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                        search_btn.click()
                    except:
                        title_field.send_keys(Keys.ENTER)
                        
                    log_message(f"   ✍️ Введено кирилицю на AbeBooks: {short_t}")
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except Exception as e:
                    log_message(f"   ⚠️ Помилка введення на AbeBooks: {e}")
                    continue
                time.sleep(random.uniform(4, 7))
                simulate_human_interaction(driver)
                close_popups(driver)

                price_val = get_product_price(driver)
                if price_val:
                    # Визначаємо валюту залежно від домену
                    currency = "$"
                    if any(x in link for x in ["yakaboo.ua", "rozetka.com", "piramidabooks.net"]):
                        currency = "грн"
                    elif "allegro.pl" in link:
                        currency = "zł"
                    elif "elefant.ro" in link:
                        currency = "lei"
                    
                    raw_price = f"{price_val} {currency}"
                    scr_name = f"scr_{i}_{idx}.png"
                    driver.save_screenshot(scr_name)
                    media = MediaFileUpload(scr_name, mimetype='image/png')
                    f = drive_service.files().create(body={'name': scr_name, 'parents': [SHARED_DRIVE_FOLDER_ID]},
                                                     media_body=media, fields='id', supportsAllDrives=True).execute()
                    img_id = f.get('id')
                    drive_service.permissions().create(fileId=img_id, body={'type': 'anyone', 'role': 'reader'},
                                                       supportsAllDrives=True).execute()
                    img_link = f"https://drive.google.com/uc?export=view&id={img_id}"
                    os.remove(scr_name)

                    formula = f'=HYPERLINK("{img_link}"; "{raw_price}")'
                    row_updates.append({
                        'range': f"{columns_map[idx]}{i}",
                        'values': [[formula]]
                    })
                    prices_found.append(price_val)
                    log_message(f"   ✅ Знайдено: {price_val} {currency}")
            except Exception as e:
                log_message(f"   ⚠️ Помилка на сайті: {e}")

        if prices_found:
            avg = round(sum(prices_found) / len(prices_found), 2)
            row_updates.append({
                'range': f"I{i}",
                'values': [[avg]]
            })
            log_message(f"   💰 Середня ціна: ${avg}")
            
        # Виконуємо пакетне оновлення для всього рядка з параметром USER_ENTERED (щоб формули працювали)
        if row_updates:
            worksheet.batch_update(row_updates, value_input_option='USER_ENTERED')


    log_message("🏁 Обробку вкладки завершено.")
    driver.quit()


if __name__ == "__main__":
    process_books()