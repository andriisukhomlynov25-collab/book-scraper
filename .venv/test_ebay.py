import os
import undetected_chromedriver as uc
import time
import sys

from config import DRIVER_PATH, CHROME_VERSION

def test_ebay(with_stealth=False):
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    # Try different arguments that might help bypass Akamai
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    
    driver = uc.Chrome(options=options, version_main=CHROME_VERSION, driver_executable_path=DRIVER_PATH)
    
    if with_stealth:
        from selenium_stealth import stealth
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
            
    try:
        # First visit ebay homepage
        print("Visiting ebay.com...")
        driver.get("https://www.ebay.com/")
        time.sleep(3)
        
        print("Visiting item page...")
        driver.get("https://www.ebay.com/itm/167355522807")
        time.sleep(3)
        
        if "Access Denied" in driver.page_source:
            print("STATUS: BLOCKED")
        else:
            print("STATUS: SUCCESS")
            print("Title:", driver.title)
    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "no_stealth"
    print(f"Running test with mode: {mode}")
    test_ebay(with_stealth=(mode=="stealth"))