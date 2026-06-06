import requests
import re
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
query = 'violity Колгосп тварин'
url = f'https://www.google.com/search?q={urllib.parse.quote(query)}'

res = requests.get(url, headers=headers)
print("Status Code:", res.status_code)
print("Length:", len(res.text))

soup = BeautifulSoup(res.text, 'html.parser')
print("Title:", soup.title.string if soup.title else None)

# Google search links are usually in div.g a
links = []
for a in soup.select('div.g a'):
    href = a.get('href', '')
    if href.startswith('http'):
        links.append(href)
        
print("Links found via 'div.g a':", len(links))
for l in links[:5]:
    print(l)

if len(links) == 0:
    # Print all external links in page
    print("All external links:")
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if href.startswith('http') and 'google.com' not in href:
            print(a.text.strip(), "->", href)
