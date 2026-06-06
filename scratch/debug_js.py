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
        
        # We will run a step-by-step JS debugger on all div.current elements!
        js_debug = """
        (function() {
            var currencyRegex = /([$£€]|zł|PLN|грн|UAH|USD|EUR|GBP|lei)/i;
            var digitRegex = /\\d/;
            var results = [];
            
            function isVisible(el) {
                var rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) return "size_zero";
                
                var style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return "style_hidden";
                
                return "ok";
            }
            
            function isExcludedParent(el) {
                var p = el;
                var excludedKeywords = [
                    'recommend', 'related', 'carousel', 'slider', 'similar', 
                    'viewed', 'sponsored', 'bought', 'merch', 'promo', 
                    'footer', 'header', 'menu', 'nav',
                    'suggestion', 'frequent', 'bundle', 'rvi-', 'vi-rec', 'sim-carousel'
                ];
                while (p && p !== document.body) {
                    if (p.tagName === 'A') {
                        var aIdClass = ((p.id || "") + " " + (p.className || "")).toLowerCase();
                        for (var kw of excludedKeywords) {
                            if (aIdClass.includes(kw)) return "link_excluded_" + kw;
                        }
                    } else {
                        var idClassText = ((p.id || "") + " " + (p.className || "")).toLowerCase();
                        for (var kw of excludedKeywords) {
                            if (idClassText.includes(kw)) return "parent_excluded_" + kw;
                        }
                    }
                    p = p.parentNode;
                }
                return "ok";
            }
            
            var elements = document.querySelectorAll('div.current');
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var text = (el.innerText || el.textContent || "").trim();
                
                var vis = isVisible(el);
                var exc = isExcludedParent(el);
                
                var style = window.getComputedStyle(el);
                var isStrikethrough = style.textDecoration.includes('line-through') || el.className.includes('original') || el.className.includes('strikethrough') || el.className.includes('listprice');
                
                results.push({
                    index: i,
                    text: text,
                    vis: vis,
                    exc: exc,
                    isStrikethrough: isStrikethrough,
                    matchesCurrency: currencyRegex.test(text),
                    matchesDigit: digitRegex.test(text),
                    textLen: text.length
                });
            }
            return results;
        })();
        """
        debug_res = driver.execute_script(js_debug)
        print("\n--- STEP BY STEP JS DEBUG FOR div.current ---")
        for item in debug_res:
            print(f"El [{item['index']}] '{item['text']}': textLen={item['textLen']}, vis={item['vis']}, exc={item['exc']}, matchesCurrency={item['matchesCurrency']}, matchesDigit={item['matchesDigit']}, strikethrough={item['isStrikethrough']}")
            
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
