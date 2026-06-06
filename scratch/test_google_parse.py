import requests
import re
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
}
res = requests.get('https://www.google.com/search?q=violity+Колгосп+тварин', headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

print("Title:", soup.title.string if soup.title else None)
for a in soup.find_all('a'):
    href = a.get('href', '')
    if href.startswith('http') or href.startswith('/url?q='):
        # Decode /url?q=
        if href.startswith('/url?q='):
            match = re.search(r'/url\?q=([^&]+)', href)
            if match:
                href = urllib.parse.unquote(match.group(1))
        if 'google' not in href:
            print("Link:", href)
