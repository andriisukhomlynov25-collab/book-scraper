import os
import sys
import time
import re

sys.path.append("/Users/getapp/PycharmProjects/book_scraper/.venv")
from stealth_scraper_ai import init_driver

driver = init_driver(instance_id=96, headless=False)
try:
    url = "https://violity.com/ua/114678091-orvell-kolgosp-tvarin-peredmova-avtora-do-cogo-vidannya-di-pi-1947"
    print(f"Navigating to {url}")
    driver.get(url)
    time.sleep(8)
    
    html = driver.page_source
    print(f"Loaded rendered HTML of length {len(html)}")
    
    # Find all occurrences of "8 000" or "8000" in rendered HTML
    matches = [m.start() for m in re.finditer(r"8\s*000", html)]
    print(f"Found {len(matches)} matches for '8 000' or '8000'")
    for idx, pos in enumerate(matches):
        start = max(0, pos - 150)
        end = min(len(html), pos + 150)
        print(f"\n--- Match {idx+1} (position {pos}) ---")
        print(html[start:end])
        
finally:
    driver.quit()
