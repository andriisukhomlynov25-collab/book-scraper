import requests
import re
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
query = 'site:violity.com Колгосп тварин'
url = f'https://www.bing.com/search?q={urllib.parse.quote(query)}'
res = requests.get(url, headers=headers)
print("Status Code:", res.status_code)
print("Text length:", len(res.text))

# Bing search results links usually match h2 class=" b_algo" or standard hrefs
matches = re.findall(r'href="([^"]+?)"', res.text)
links_found = 0
for link in matches:
    if 'violity.com' in link and 'search' not in link:
        print("Found Link:", link)
        links_found += 1

if links_found == 0:
    print("No links found. Snippet:")
    print(res.text[:1000])
