import os
import re
import time
import random
import threading
import requests
import urllib.parse
import gspread
import undetected_chromedriver as uc
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# ================= НАЛАШТУВАННЯ =================
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = '1F1KctUExEnsh9uZpLxcID6HgY1gxkv5fiuvXGMOYw5s'
SHARED_DRIVE_FOLDER_ID = '0AHvgRKQpv3qrUk9PVA'
# =================================================
# Додайте сюди ваші ключі Serper API.
SERPER_API_KEYS = [
    '18a31827f8487bd89b2303ca8dea91faddeace0c',
    # 'ВАШ_ДРУГИЙ_КЛЮЧ',
]
current_key_index = 0
# =================================================

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
sheet_client = gspread.authorize(creds)
spreadsheet = sheet_client.open_by_key(SPREADSHEET_ID)

# undetected_chromedriver патчить один файл chromedriver — при паралельному старті
# кількох потоків виникає race condition. Лок захищає тільки момент init.
_driver_init_lock = threading.Lock()


def log_message(message):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] {message}")


from config import DRIVER_PATH, CHROME_VERSION

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    with _driver_init_lock:
        return uc.Chrome(options=options, version_main=CHROME_VERSION, driver_executable_path=DRIVER_PATH)


def simulate_human_interaction(driver):
    try:
        actions = ActionChains(driver)
        for _ in range(random.randint(2, 5)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            try:
                actions.move_by_offset(x_offset, y_offset).perform()
                time.sleep(random.uniform(0.1, 0.3))
            except:
                actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
    except:
        pass


def set_amazon_location(driver):
    try:
        driver.get("https://www.amazon.com/")
        time.sleep(random.uniform(3, 5))
        try:
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
    css_selectors = [
        "button[aria-label='Close']",
        ".main-pwa-close-button",
        "#sp-cc-accept",
        ".pm-close-button",
        "button.cm-banner__close",
        "a[data-test='close-guest-modal']",
        ".modal-close",
        ".ui-btn-close",
        "button[data-role='accept-consent']",
        "#gdpr-banner-accept",
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
        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'acceptă')]",
        "//button[contains(text(), 'OK')]",
        "//button[contains(text(), 'Ok')]",
        "//span[contains(text(), 'Close')]",
        "//span[contains(text(), 'Закрити')]",
        "//*[contains(@class, 'close') and contains(@class, 'button')]",
        "//*[contains(@id, 'cookie') or contains(@class, 'cookie')]//button"
    ]

    for _ in range(2):
        for selector in css_selectors:
            try:
                for el in driver.find_elements(By.CSS_SELECTOR, selector):
                    if el.is_displayed():
                        driver.execute_script("arguments[0].click();", el)
                        log_message(f"   🧹 Закрито банер (CSS): {selector}")
                        time.sleep(0.5)
            except:
                pass
        for xpath in xpath_selectors:
            try:
                for el in driver.find_elements(By.XPATH, xpath):
                    if el.is_displayed():
                        driver.execute_script("arguments[0].click();", el)
                        log_message("   🧹 Закрито банер (XPath)")
                        time.sleep(0.5)
            except:
                pass


def select_paper_format(driver):
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
    for xpath in paper_xpaths:
        try:
            for el in driver.find_elements(By.XPATH, xpath):
                if el.is_displayed():
                    el.click()
                    log_message("   📖 Обрано паперовий формат книги.")
                    time.sleep(1.5)
                    return
        except:
            pass


def get_product_price(driver):
    try:
        select_paper_format(driver)

        page_source = driver.page_source
        if "Access Denied" in page_source or "Checking your browser" in page_source:
            log_message("   🛡️ Виявлено блок (Access Denied / Cloudflare). Пропуск...")
            return None

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

        selectors = [
            # Amazon
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
            # Yakaboo
            ".product-price",
            ".base-product__price",
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
            # Fallbacks
            ".price",
            "[class*='price']"
        ]

        price_text = None
        current_url = driver.current_url

        if "allegro.pl" in current_url:
            text = driver.find_element(By.TAG_NAME, "body").text
            m = re.search(r'(\d+[\s,]\d{2}\s*zł)', text)
            if m:
                price_text = m.group(1)
        elif "thriftbooks.com" in current_url:
            text = driver.find_element(By.TAG_NAME, "body").text
            m = re.search(r'\$(\d+[.,]\d{2})', text)
            if m:
                price_text = m.group(1)
        elif "olx." in current_url:
            text = driver.find_element(By.TAG_NAME, "body").text
            m = re.search(r'(\d+[\s\d,]*(?:zł|грн))', text)
            if m:
                price_text = m.group(1)

        if not price_text:
            for sel in selectors:
                try:
                    for element in driver.find_elements(By.CSS_SELECTOR, sel):
                        if element.is_displayed():
                            text = element.get_attribute("innerText") or element.text
                            if text and any(c.isdigit() for c in text):
                                if "hup.harvard.edu" in current_url and "•" in text:
                                    text = text.split("•")[0]
                                price_text = text
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});", element
                                )
                                time.sleep(0.5)
                                break
                    if price_text:
                        break
                except:
                    continue

        if price_text:
            if '-' in price_text:
                price_text = price_text.split('-')[0]
            elif ' to ' in price_text.lower():
                price_text = price_text.lower().split(' to ')[0]

            clean_price = re.sub(r'[^\d.,]', '', price_text).replace(',', '.')
            if clean_price.count('.') > 1:
                parts = clean_price.split('.')
                clean_price = "".join(parts[:-1]) + "." + parts[-1]
            if clean_price:
                return float(clean_price)
    except:
        pass
    return None


# ─────────────────────────────────────────────────────────────
#  Функція для одного потоку: один лінк → одна ціна
# ─────────────────────────────────────────────────────────────
def scrape_single_link(link, book_title, row_idx, link_idx, year="", is_rare=False):
    # Кожен потік будує свій drive_service (httplib2 не є thread-safe)
    thread_drive = build('drive', 'v3', credentials=creds)
    driver = init_driver()
    try:
        # Amazon: налаштовуємо локацію USA перед переходом на товар
        if "amazon.com" in link:
            set_amazon_location(driver)

        # eBay: «прогрів» через головну сторінку
        if "ebay.com" in link:
            log_message(f"   [#{link_idx}] 🛡️ Прогрів eBay...")
            driver.get("https://www.ebay.com/")
            time.sleep(random.uniform(2, 4))

        log_message(f"   [#{link_idx}] 🔗 {link[:60]}...")
        driver.get(link)

        # AbeBooks: вводимо назву вручну (для кириличних заголовків)
        if "abebooks.com/servlet/SearchEntry" in link:
            try:
                abe_wait = WebDriverWait(driver, 10)
                abe_wait.until(EC.presence_of_element_located((By.NAME, "tn")))
                title_field = driver.find_element(By.NAME, "tn")
                title_field.clear()
                clean_t = re.sub(r'[^a-zA-Zа-яА-ЯёЁєЄіІїЇґҐ0-9\s]', ' ', book_title)
                short_t = " ".join(clean_t.split()[:6]).strip()
                if is_rare and year:
                    short_t = f"{short_t} {year}"
                title_field.send_keys(short_t)
                try:
                    search_btn = driver.find_element(
                        By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
                    )
                    search_btn.click()
                except:
                    title_field.send_keys(Keys.ENTER)
                log_message(f"   [#{link_idx}] ✍️ AbeBooks: {short_t}")
                abe_wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except Exception as e:
                log_message(f"   [#{link_idx}] ⚠️ Помилка AbeBooks: {e}")
                return None

        time.sleep(random.uniform(4, 7))
        simulate_human_interaction(driver)
        close_popups(driver)

        price_val = get_product_price(driver)
        if not price_val:
            log_message(f"   [#{link_idx}] — ціну не знайдено")
            return None

        currency = "$"
        if any(x in link for x in ["yakaboo.ua", "rozetka.com", "piramidabooks.net", "rvv-kniga.com", "olx.ua"]):
            currency = "грн"
        elif "allegro.pl" in link:
            currency = "zł"
        elif "elefant.ro" in link:
            currency = "lei"

        raw_price = f"{price_val} {currency}"
        scr_name = f"scr_{row_idx}_{link_idx}.png"
        driver.save_screenshot(scr_name)

        media = MediaFileUpload(scr_name, mimetype='image/png')
        f = thread_drive.files().create(
            body={'name': scr_name, 'parents': [SHARED_DRIVE_FOLDER_ID]},
            media_body=media, fields='id', supportsAllDrives=True
        ).execute()
        img_id = f.get('id')
        thread_drive.permissions().create(
            fileId=img_id,
            body={'type': 'anyone', 'role': 'reader'},
            supportsAllDrives=True
        ).execute()
        img_link = f"https://drive.google.com/uc?export=view&id={img_id}"
        os.remove(scr_name)

        log_message(f"   [#{link_idx}] ✅ {price_val} {currency}")
        return {
            'link_idx': link_idx,
            'price_val': price_val,
            'formula': f'=HYPERLINK("{img_link}"; "{raw_price}")'
        }

    except Exception as e:
        log_message(f"   [#{link_idx}] ⚠️ Помилка: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass


# ─────────────────────────────────────────────────────────────
#  Головна функція
# ─────────────────────────────────────────────────────────────
def process_books():
    worksheet = spreadsheet.sheet1
    log_message(f"📑 Обробка вкладки: '{worksheet.title}'")

    records = worksheet.get_all_values()[1:]
    columns_map = {0: 'F', 1: 'G', 2: 'H'}

    regular_sites = [
        "amazon.com", "ebay.com", "abebooks.com",
        "biblio.com", "globusbooks.com", "hup.harvard.edu",
        "allegro.pl", "booksamillion.com", "thriftbooks.com",
        "yakaboo.ua", "piramidabooks.net", "elefant.ro", "rozetka.com.ua"
    ]
    # Сайти для раритетних/антикварних видань: фокус на Україну та Європу
    rare_sites = [
        "yakaboo.ua", "rozetka.com.ua", "olx.ua", "rvv-kniga.com",
        "allegro.pl", "abebooks.com", "biblio.com",
    ]

    for i, row in enumerate(records, start=2):
        if len(row) < 3 or not row[2]:
            continue
        if "список цінних видань" in row[0].lower():
            continue

        book_title = row[2]
        year = row[3].strip() if len(row) > 3 else ""
        is_rare = year.isdigit() and int(year) < 1970

        if is_rare:
            log_message(f"📘 Рядок {i} [раритет {year}]: {book_title[:50]}...")
        else:
            log_message(f"📘 Рядок {i}: {book_title[:50]}...")

        # --- SERPER: знаходимо посилання ---
        try:
            if is_rare:
                search_sites = rare_sites
                site_query = " OR ".join([f"site:{s}" for s in search_sites])
                search_query = f"{book_title} {year} ({site_query}) -reprint -facsimile"
            else:
                search_sites = regular_sites
                site_query = " OR ".join([f"site:{s}" for s in search_sites])
                search_query = f"{book_title} price ({site_query})"

            allowed_domains = [s.split('.')[0] for s in search_sites]
            res = get_serper_data(search_query)
            all_items = res.get('organic', []) if res else []

            links = []
            seen_domains = set()
            for item in all_items:
                link = item['link']
                domain = urllib.parse.urlparse(link).netloc.lower()
                if any(base in domain for base in allowed_domains) and domain not in seen_domains:
                    if "abebooks.com" in domain and any(ord(c) > 127 for c in link):
                        continue
                    links.append(link)
                    seen_domains.add(domain)
                if len(links) >= 3:
                    break

            if "abebooks.com" not in seen_domains and len(links) < 3:
                links.append("https://www.abebooks.com/servlet/SearchEntry")

        except Exception as e:
            log_message(f"   ⚠️ Помилка Serper: {e}")
            links = []

        if not links:
            continue

        log_message(f"   🌐 Знайдено {len(links)} сайт(и). Запускаємо паралельно...")

        # --- ПАРАЛЕЛЬНИЙ SCRAPING: кожен лінк у своєму потоці ---
        row_updates = []
        prices_found = []

        with ThreadPoolExecutor(max_workers=len(links)) as executor:
            futures = {
                executor.submit(scrape_single_link, link, book_title, i, idx, year, is_rare): idx
                for idx, link in enumerate(links)
            }
            for future in as_completed(futures):
                result = future.result()
                if result:
                    col = columns_map.get(result['link_idx'])
                    if col:
                        row_updates.append({
                            'range': f"{col}{i}",
                            'values': [[result['formula']]]
                        })
                    prices_found.append(result['price_val'])

        # --- ЗАПИС У ТАБЛИЦЮ (з головного потоку) ---
        if prices_found:
            avg = round(sum(prices_found) / len(prices_found), 2)
            row_updates.append({'range': f"I{i}", 'values': [[avg]]})
            log_message(f"   💰 Середня ціна: {avg}")

        if row_updates:
            worksheet.batch_update(row_updates, value_input_option='USER_ENTERED')

    log_message("🏁 Обробку вкладки завершено.")


if __name__ == "__main__":
    process_books()
