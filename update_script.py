import re

with open('.venv/foreign_price_scraper_ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports and API key
import_block = """import sys
import os
import re
import time
import random
import urllib.parse
import argparse
import requests
import gspread
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from openai import OpenAI
from pydantic import BaseModel"""

content = re.sub(r'import sys.*?import undetected_chromedriver as uc', import_block, content, flags=re.DOTALL)

config_add = """SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"  # <--- ВСТАВТЕ ВАШ КЛЮЧ ТУТ
TWOCAPTCHA_API_KEY = "780e6839764f3a71fa50946f0c4b2315"
"""
content = re.sub(r"SCOPE = \['https://spreadsheets\.google\.com/feeds', 'https://www\.googleapis\.com/auth/drive'\]\nTWOCAPTCHA_API_KEY = .*?\n", config_add, content)

# 2. Add OpenAI function
openai_func = """
class BookLink(BaseModel):
    site: str
    url: str

class BookLinksResponse(BaseModel):
    links: list[BookLink]

def get_links_from_openai(title, year):
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        log_message("❌ Не вказано OPENAI_API_KEY. Будь ласка, вставте ваш ключ у змінну OPENAI_API_KEY (рядок 27).")
        return []
        
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"Знайди 3 ціни з посиланнями на них по кожній книзі зі списку:\\nНазва: {title}\\nРік: {year}\\n\\nШукай на сайтах ebay.com, amazon.com, abebooks.com, biblio.com. Поверни прямі URL на сторінки товарів."
    
    try:
        log_message("🤖 Запит до OpenAI для отримання посилань...")
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that searches for book prices and returns direct URLs. Return only valid URLs to book product pages."},
                {"role": "user", "content": prompt}
            ],
            response_format=BookLinksResponse,
            temperature=0.3
        )
        response = completion.choices[0].message.parsed
        
        valid_links = []
        for item in response.links:
            if "http" in item.url:
                site = item.site.lower()
                if 'ebay' in item.url: site = 'ebay.com'
                elif 'amazon' in item.url: site = 'amazon.com'
                elif 'abebooks' in item.url: site = 'abebooks.com'
                elif 'biblio' in item.url: site = 'biblio.com'
                valid_links.append({"site": site, "url": item.url})
                
        log_message(f"✅ OpenAI повернув {len(valid_links)} посилань.")
        for link in valid_links:
            log_message(f"   🔗 {link['site']}: {link['url']}")
        return valid_links
    except Exception as e:
        log_message(f"⚠️ Помилка виклику OpenAI: {e}")
        return []

"""

# Insert before get_search_sites_by_year
content = content.replace("def get_search_sites_by_year(row_data):", openai_func + "\ndef get_search_sites_by_year(row_data):")

# 3. Update process_product_page to handle 404
process_start = "def process_product_page(driver, url, site_type, row_idx, col_char, target_title):"
process_repl = """def process_product_page(driver, url, site_type, row_idx, col_char, target_title):
    \"\"\"
    Loads product page, verifies product matches, extracts price, takes a styled screenshot with a banner,
    uploads to Google Drive, and returns the Sheets formula.
    \"\"\"
    try:
        log_message(f"🔗 Перехід за посиланням ({site_type.upper()}): {url[:80]}...")
        driver.get(url)
        time.sleep(4)
        close_popups(driver)
        
        # Перевірка на 404 або неробочі посилання ("мусорні" посилання ШІ)
        page_source = driver.page_source.lower()
        if "404 not found" in page_source or "page not found" in page_source or "we don't know that page" in page_source:
            log_message(f"🗑️ Виявлено 'мусорне' посилання (404/Not Found): {url}")
            return None, None
            
        current_url_after_redirect = driver.current_url
        if "sorry/index" in current_url_after_redirect or "google.com/sorry" in current_url_after_redirect:
             log_message(f"🛑 Капча на сторінці: {url}")
             handle_captcha(driver, "Магазинний браузер")"""
content = content.replace(process_start + "\n    \"\"\"\n    Loads product page, verifies product matches, extracts price, takes a styled screenshot with a banner,\n    uploads to Google Drive, and returns the Sheets formula.\n    \"\"\"\n    try:\n        log_message(f\"ðŸ”— ÐŸÐµÑ€ÐµÑ ід за посиланням ({site_type.upper()}): {url[:60]}...\")\n        driver.get(url)\n        time.sleep(4)\n        close_popups(driver)\n", process_repl)


# 4. Modify main loop to use OpenAI instead of get_search_sites_by_year / find_link_parallel
main_loop_start = """            search_sites = get_search_sites_by_year(row_data)
            matches = []

            for site in search_sites:
                if len(matches) >= len(empty_cols):
                    break
                log_message(f"🔍 Пошук на сайті {site}...")
                try:
                    url, resolved_title = find_link_parallel(driver_store, driver_search, site, title)
                    if url:
                        col_char = col_chars[empty_cols[len(matches)]]
                        formula, price = process_product_page(driver_store, url, site, i, col_char, resolved_title)
                        if formula:
                            matches.append({'site': site, 'price': price, 'formula': formula, 'url': url})
                            log_message(f"✅ Знайдено ціну на {site}: {price}")
                    else:
                        log_message(f"❌ Не знайдено книги на {site}")
                except Exception as err:
                    log_message(f"⚠️ Помилка пошуку на {site}: {err}")"""

main_loop_repl = """            matches = []
            ai_links = get_links_from_openai(title, col_d)
            
            for link_info in ai_links:
                if len(matches) >= len(empty_cols):
                    break
                    
                site = link_info['site']
                url = link_info['url']
                log_message(f"🔍 Перевірка посилання від OpenAI ({site}): {url[:80]}...")
                
                try:
                    col_char = col_chars[empty_cols[len(matches)]]
                    # We pass 'title' directly for verification since OpenAI gives direct links
                    formula, price = process_product_page(driver_store, url, site, i, col_char, title)
                    if formula:
                        matches.append({'site': site, 'price': price, 'formula': formula, 'url': url})
                        log_message(f"✅ Знайдено ціну на {site}: {price}")
                    else:
                        log_message(f"❌ Посилання не пройшло перевірку або не містить ціни.")
                except Exception as err:
                    log_message(f"⚠️ Помилка обробки посилання {url}: {err}")"""

# Because of character encoding issues in my matching, I will use regex to replace it
content = re.sub(r'            search_sites = get_search_sites_by_year\(row_data\).*?except Exception as err:\n                    log_message\(f"\\u26a0\\ufe0f Помилка пошуку на \{site\}: \{err\}"\)', main_loop_repl, content, flags=re.DOTALL)

with open('.venv/foreign_price_scraper_ai.py', 'w', encoding='utf-8') as f:
    f.write(content)
