import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

try:
    sys.path.append(PARENT_DIR)
    from config import DRIVER_PATH, CHROME_VERSION
except ImportError:
    DRIVER_PATH = None
    CHROME_VERSION = 148

def init_driver(instance_id=555, headless=True):
    options = uc.ChromeOptions()
    profile_dir = os.path.join(PARENT_DIR, f'auto_hotkey_chrome_profile_{instance_id}')
    os.makedirs(profile_dir, exist_ok=True)
    
    lock_file = os.path.join(profile_dir, 'SingletonLock')
    if os.path.islink(lock_file) or os.path.exists(lock_file):
        try: os.unlink(lock_file)
        except:
            try: os.remove(lock_file)
            except: pass
            
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--window-size=1600,1000")
    options.add_argument("--disable-notifications")
    
    chrome_kwargs = {'options': options, 'headless': headless}
    if CHROME_VERSION:
        chrome_kwargs['version_main'] = CHROME_VERSION
    if DRIVER_PATH:
        chrome_kwargs['driver_executable_path'] = DRIVER_PATH
    return uc.Chrome(**chrome_kwargs)

def main():
    driver = init_driver(instance_id=555, headless=False)
    try:
        print("Warming up Violity domain...")
        driver.get("https://violity.com")
        time.sleep(5)
        print(f"Warmed up! URL: {driver.current_url}")
        
        url = "https://violity.com/ru/113903127-b-krupnickij-teoriya-rimu-i-shlyahi-rosijskoyi-istoriografiyi-myunhen-1952-diaspora"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(5)
        
        print(f"Loaded! URL: {driver.current_url}")
        print(f"Page Title: {driver.title}")
        
        # Search for elements containing "250" or "грн"
        print("Searching for elements...")
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), '250') or contains(text(), 'грн')]")
        print(f"Found {len(elements)} candidates:")
        for idx, el in enumerate(elements):
            try:
                tag = el.tag_name
                text = el.text or el.get_attribute("innerText")
                clazz = el.get_attribute("class")
                id_ = el.get_attribute("id")
                parent_tag = el.find_element(By.XPATH, "..").tag_name
                parent_class = el.find_element(By.XPATH, "..").get_attribute("class")
                print(f"[{idx}] Tag: {tag}, Class: {clazz}, ID: {id_}, Text: '{text.strip()}' | Parent: {parent_tag} ({parent_class})")
            except Exception as e:
                print(f"[{idx}] Error reading element: {e}")
                
        # Let's run find_all_price_elements JS script to see if it lists anything
        js_find = """
        (function() {
            var currencyRegex = /([$£€]|zł|PLN|грн|UAH|USD|EUR|GBP|lei)/i;
            var digitRegex = /\\d/;
            var list = [];
            var elements = document.querySelectorAll('span, div, p, b, strong, font, td, h1, h2, h3, h4');
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var text = (el.innerText || el.textContent || "").trim();
                if (!text || text.length > 35) continue;
                if (currencyRegex.test(text) && digitRegex.test(text)) {
                    list.push({
                        tag: el.tagName,
                        clazz: el.className,
                        text: text,
                        visible: el.getBoundingClientRect().width > 0
                    });
                }
            }
            return list;
        })();
        """
        js_res = driver.execute_script(js_find)
        print("\\n--- JS Candidate Search ---")
        if js_res:
            for item in js_res:
                print(item)
        else:
            print("No candidates found via JS")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
