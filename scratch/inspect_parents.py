import os
import time
import sys
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def init_driver(instance_id=555, headless=False):
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
    chrome_kwargs['version_main'] = 148
    return uc.Chrome(**chrome_kwargs)

def main():
    driver = init_driver(instance_id=555, headless=False)
    try:
        print("Warming up Violity...")
        driver.get("https://violity.com")
        time.sleep(5)
        
        url = "https://violity.com/ru/113903127-b-krupnickij-teoriya-rimu-i-shlyahi-rosijskoyi-istoriografiyi-myunhen-1952-diaspora"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(5)
        
        # Find the specific element
        print("\nFinding elements with class 'current'...")
        elements = driver.find_elements(By.CSS_SELECTOR, "div.current")
        print(f"Found {len(elements)} elements with class 'current'")
        
        for idx, el in enumerate(elements):
            text = (el.text or el.get_attribute("innerText")).strip()
            print(f"\n--- Element [{idx}] (Text: '{text}') ---")
            
            # Print ancestor chain
            curr = el
            chain = []
            while curr and curr.tag_name != 'html':
                try:
                    tag = curr.tag_name
                    clazz = curr.get_attribute("class") or ""
                    id_ = curr.get_attribute("id") or ""
                    chain.append((tag, clazz, id_))
                    
                    # Move to parent
                    curr = curr.find_element(By.XPATH, "..")
                except Exception as e:
                    print(f"Error traversing parent: {e}")
                    break
                    
            # Print chain from leaf to root
            for depth, node in enumerate(chain):
                tag, clazz, id_ = node
                match_keywords = []
                excludedKeywords = [
                    'recommend', 'related', 'carousel', 'slider', 'similar', 
                    'viewed', 'sponsored', 'bought', 'merch', 'promo', 
                    'footer', 'header', 'menu', 'nav',
                    'suggestion', 'frequent', 'bundle', 'rvi-', 'vi-rec', 'sim-carousel'
                ]
                idClassText = f"{id_} {clazz}".lower()
                for kw in excludedKeywords:
                    if kw in idClassText:
                        match_keywords.append(kw)
                
                match_str = f" <- MATCHES EXCLUSION: {match_keywords}" if match_keywords else ""
                print(f"  Level {depth}: <{tag} class='{clazz}' id='{id_}'>{match_str}")
                
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
