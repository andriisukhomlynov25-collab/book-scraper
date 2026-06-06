import urllib.parse
import requests
import re

def search_yahoo(query):
    print(f"\n--- Searching Yahoo for: '{query}' ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}"
    res = requests.get(url, headers=headers, timeout=10)
    matches = re.findall(r'href="([^"]+?)"', res.text)
    
    yahoo_results = []
    for link in matches:
        if 'r.search.yahoo.com' in link:
            match = re.search(r'/RU=([^/]+)', link)
            if match:
                decoded_url = urllib.parse.unquote(match.group(1))
                if decoded_url.startswith("http") and "yahoo.com" not in decoded_url and "yimg.com" not in decoded_url and decoded_url not in yahoo_results:
                    yahoo_results.append(decoded_url)
                    print(decoded_url)
    return yahoo_results

q1 = '"Колгосп тварин" Мюнхен 1947'
search_yahoo(q1)

q2 = '"Колгосп тварин" Мюнхен 1947 violity'
search_yahoo(q2)

q3 = '"Колгосп тварин" Мюнхен 1947 купить'
search_yahoo(q3)
