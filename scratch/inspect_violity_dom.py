import os
import sys
import time

sys.path.append("/Users/getapp/PycharmProjects/book_scraper/.venv")
from stealth_scraper_ai import init_driver

driver = init_driver(instance_id=97, headless=False)
try:
    url = "https://violity.com/ua/114678091-orvell-kolgosp-tvarin-peredmova-avtora-do-cogo-vidannya-di-pi-1947"
    print(f"Navigating to {url}")
    driver.get(url)
    time.sleep(8)
    
    title = driver.title
    print(f"Loaded Page Title: {title}")
    
    # Save screenshot to inspect visually
    os.makedirs("/Users/getapp/PycharmProjects/book_scraper/scratch", exist_ok=True)
    screenshot_path = "/Users/getapp/PycharmProjects/book_scraper/scratch/violity_dom_test.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    # Dump page source to see if we got content
    page_source = driver.page_source
    print(f"Page Source length: {len(page_source)} chars")
    
    # Try finding elements containing UAH or грн
    # In Ukraine it is typical to display price as e.g. "1 500 грн" or "1500 ₴" or similar.
    # Let's run a small JS script to find elements with numbers and currency symbols
    js_script = """
    (function() {
        var elms = document.querySelectorAll('span, div, p, b, strong, td, h1, h2, h3, h4');
        var results = [];
        for (var i = 0; i < elms.length; i++) {
            var text = (elms[i].innerText || elms[i].textContent || "").trim();
            if (text.includes('грн') || text.includes('₴') || text.includes('USD') || text.includes('$')) {
                results.push({
                    tag: elms[i].tagName,
                    id: elms[i].id,
                    className: elms[i].className,
                    text: text.substring(0, 50)
                });
            }
        }
        return results.slice(0, 30);
    })();
    """
    elements = driver.execute_script(js_script)
    print("\n--- Elements containing currency markers ---")
    for el in elements:
        print(f"[{el['tag']}] ID: {el['id']} | Class: {el['className']} | Text: '{el['text']}'")

finally:
    driver.quit()
