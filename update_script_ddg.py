import re

with open('.venv/foreign_price_scraper_ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

ddg_func = """
from ddgs import DDGS
import time

def get_links_from_ddg(title, year):
    valid_links = []
    
    # We will search each site individually to get the best result
    sites = ["ebay.com", "amazon.com", "abebooks.com", "biblio.com"]
    query_core = f"{title} {year}".strip()
    
    log_message(f"🦆 Запит до DuckDuckGo для пошуку прямих посилань...")
    
    with DDGS() as ddgs:
        for site in sites:
            query = f"site:{site} {query_core}"
            try:
                # Get top 2 results per site
                results = ddgs.text(query, max_results=2)
                for res in results:
                    href = res.get('href', '')
                    if href and site in href.lower():
                        # Exclude obvious non-product pages
                        noise = ['/search', '/help', '/contact', '/policy', '/category', '/cart', '/account', '/join', '/terms', '/privacy', '/about', 'search.php']
                        if not any(n in href.lower() for n in noise):
                            valid_links.append({"site": site, "url": href})
                            break # Just take the first good one per site
                time.sleep(1.5) # Be polite to DDG
            except Exception as e:
                log_message(f"⚠️ Помилка пошуку DuckDuckGo для {site}: {e}")
                
    log_message(f"✅ DuckDuckGo повернув {len(valid_links)} унікальних посилань.")
    for link in valid_links:
        log_message(f"   🔗 {link['site']}: {link['url']}")
        
    return valid_links
"""

# Replace the OpenAI imports and function
content = re.sub(r'from openai import OpenAI\nfrom pydantic import BaseModel', '', content)
content = re.sub(r'class BookLink.*?return \[\]\n\n', ddg_func, content, flags=re.DOTALL)

# Replace ai_links call
content = content.replace("ai_links = get_links_from_openai(title, col_d)", "ai_links = get_links_from_ddg(title, col_d)")
content = content.replace("OpenAI", "DuckDuckGo")

with open('.venv/foreign_price_scraper_ddg.py', 'w', encoding='utf-8') as f:
    f.write(content)
