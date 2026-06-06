import requests
import re
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
query = 'violity Колгосп тварин'
url = f'https://search.yahoo.com/search?p={urllib.parse.quote(query)}'

res = requests.get(url, headers=headers)
print("Status Code:", res.status_code)
print("Length:", len(res.text))

soup = BeautifulSoup(res.text, 'html.parser')
print("Title:", soup.title.string if soup.title else None)

# Yahoo search links are usually inside h3 class="title" a or standard anchors
links = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    if href.startswith('http') and 'yahoo.com' not in href and 'yimg.com' not in href:
        links.append(href)
        
print("Yahoo External Links found:", len(links))
for l in links[:15]:
    print(l)
