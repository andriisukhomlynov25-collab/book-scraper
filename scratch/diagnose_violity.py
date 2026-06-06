import sys
import time
import os
from selenium.webdriver.common.by import By

# Add the .venv directory to path to import stealth_scraper_ai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.venv')))

from stealth_scraper_ai import init_driver, parse_price

def main():
    print("Initializing driver...")
    driver = init_driver(instance_id=555, headless=True)
    try:
        # Domain warm-up first to set cookies and bypass Cloudflare
        print("Warming up domain violity.com...")
        driver.get("https://violity.com")
        time.sleep(5)
        
        url = "https://violity.com/ru/113903127-b-krupnickij-teoriya-rimu-i-shlyahi-rosijskoyi-istoriografiyi-myunhen-1952-diaspora"
        print(f"Loading URL: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Save a screenshot for manual check
        screenshot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../scratch_test_violity.png"))
        driver.save_screenshot(screenshot_path)
        print(f"Saved screenshot to {screenshot_path}")
        
        # Get page source and elements
        print(f"Current URL: {driver.current_url}")
        print("Page title:", driver.title)
        
        # Print some interesting elements
        print("\n--- Searching for elements ---")
        
        # 1. Let's find all text on the page to verify if we loaded it successfully
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"Body text length: {len(body_text)}")
        if "грн" in body_text:
            print("FOUND 'грн' in body text!")
        else:
            print("NOT FOUND 'грн' in body text!")
            # Print a snippet of body text
            print("Snippet of body text:", body_text[:500])
            
        # 2. Find any element containing "грн" using XPath
        grn_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'грн')]")
        print(f"Elements containing 'грн' by XPath text(): {len(grn_elements)}")
        for i, el in enumerate(grn_elements[:15]):
            try:
                print(f"[{i}] <{el.tag_name} class='{el.get_attribute('class')}'>: '{el.text}'")
            except: pass
            
        # 3. Find any element containing "грн" using innerText via JS search
        elements_with_grn_js = driver.execute_script("""
            var els = document.querySelectorAll('*');
            var results = [];
            for (var i = 0; i < els.length; i++) {
                var el = els[i];
                var text = (el.innerText || el.textContent || "").trim();
                if (text.includes("грн") && text.length < 100) {
                    // check if it has children with "грн"
                    var hasChildWithGrn = false;
                    for (var j = 0; j < el.children.length; j++) {
                        if ((el.children[j].innerText || el.children[j].textContent || "").includes("грн")) {
                            hasChildWithGrn = true;
                            break;
                        }
                    }
                    results.push({
                        tag: el.tagName,
                        className: el.className,
                        text: text,
                        hasChildWithGrn: hasChildWithGrn,
                        id: el.id
                    });
                }
            }
            return results;
        """)
        print(f"\nElements containing 'грн' by JS: {len(elements_with_grn_js)}")
        for i, res in enumerate(elements_with_grn_js[:20]):
            print(f"[{i}] <{res['tag']} class='{res['className']}' id='{res['id']}'> hasChild={res['hasChildWithGrn']}: '{res['text']}'")
            
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
