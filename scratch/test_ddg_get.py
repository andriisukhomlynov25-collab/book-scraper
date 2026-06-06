import requests
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
}
query = 'site:violity.com Колгосп тварин'
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'
res = requests.get(url, headers=headers)
print("Status Code:", res.status_code)
print("Text length:", len(res.text))

matches = re.findall(r'href=[\'"]([^\'"]+?)[\'"]', res.text)
links_found = 0
for link in matches:
    if 'uddg=' in link:
        match = re.search(r'uddg=([^&]+)', link)
        if match:
            decoded = urllib.parse.unquote(match.group(1))
            print("Found URL:", decoded)
            links_found += 1

if links_found == 0:
    print("No links found. Snippet of HTML:")
    print(res.text[:1000])
