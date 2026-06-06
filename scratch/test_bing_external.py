import requests
import re
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
query = 'Колгосп тварин 1947'
url = f'https://www.bing.com/search?q={urllib.parse.quote(query)}'
res = requests.get(url, headers=headers)

# Find all hrefs
matches = re.findall(r'href="([^"]+?)"', res.text)
print(f"Total hrefs found: {len(matches)}")
for link in matches:
    if link.startswith('http') and 'bing.com' not in link and 'microsoft.com' not in link and 'live.com' not in link:
        print("External Link:", link)
