import requests

url = "https://violity.com/ru/111423016-lyubavskij-m-k-ocherk-istorii-litovsko-russkogo-gosudarstva-do-lyublinskoj-unii"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
res = requests.get(url, headers=headers, allow_redirects=True)
print(f"Final URL: {res.url}")
print(f"Status Code: {res.status_code}")
print(f"HTML snippet: {res.text[:1000]}")
