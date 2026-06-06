import requests
import re
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
query = 'site:violity.com Колгосп тварин'
url = f'https://www.bing.com/search?q={urllib.parse.quote(query)}'
res = requests.get(url, headers=headers)

# Find all hrefs
matches = re.findall(r'href="([^"]+?)"', res.text)
print(f"Total hrefs found: {len(matches)}")
for link in matches[:100]:
    if 'violity.com' in link or 'violity' in link or 'ck/a' in link:
        print("Link:", link)
