import os
import time
import sys
import random
from selenium import webdriver
import undetected_chromedriver as uc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

try:
    sys.path.append(PARENT_DIR)
    from config import DRIVER_PATH, CHROME_VERSION
except ImportError:
    DRIVER_PATH = None
    CHROME_VERSION = 148

def init_driver(instance_id=123, headless=False):
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
    print("Initializing driver...")
    driver = init_driver(instance_id=123, headless=False)
    try:
        print("Navigating to Violity home page...")
        driver.get("https://violity.com")
        time.sleep(5)
        print(f"Current URL: {driver.current_url}")
        print(f"Page Title: {driver.title}")
        
        print("Navigating to Row 3 Listing 2...")
        driver.get("https://violity.com/ua/108950355-ocherk-istorii-litovsko-russkogo-gosudarstva-do-lyublinskoj-unii-vklyuchitelno-m-k-lyubavskij")
        time.sleep(5)
        print(f"Current URL: {driver.current_url}")
        print(f"Page Title: {driver.title}")
        
        driver.save_screenshot(os.path.join(PARENT_DIR, "scratch_test_violity.png"))
        print("Screenshot saved to scratch_test_violity.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
