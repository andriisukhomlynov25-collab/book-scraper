import requests
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}
res = requests.get('https://www.bing.com/search?q=orwell', headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

print("Title:", soup.title.string if soup.title else None)
results = soup.select('li.b_algo h2 a')
print("Total result links found via selector 'li.b_algo h2 a':", len(results))
for r in results:
    print(r.text, "->", r.get('href'))

# Fallback print all external links from soup
print("\n--- All external links in page ---")
for link in soup.find_all('a'):
    href = link.get('href', '')
    if href.startswith('http') and 'bing.com' not in href and 'microsoft' not in href and 'live.com' not in href:
        print(link.text.strip(), "->", href)
