import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
query = 'violity Колгосп тварин'
url = f'https://search.yahoo.com/search?p={urllib.parse.quote(query)}'
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

print("Title:", soup.title.string if soup.title else None)

for a in soup.find_all('a'):
    href = a.get('href', '')
    if 'r.search.yahoo.com' in href:
        # Decode the target URL from Yahoo redirect link
        # Yahoo format: https://r.search.yahoo.com/_ylt=.../RV=2/RE=.../RO=10/RU=DECODED_URL/RK=2/RS=...
        match = re.search(r'/RU=([^/]+)', href)
        if match:
            decoded = urllib.parse.unquote(match.group(1))
            print("Found URL:", decoded)
