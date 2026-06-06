import requests
import urllib.parse

instances = [
    "https://searx.be",
    "https://priv.au",
    "https://search.disroot.org",
    "https://baresearch.org",
    "https://searx.space"
]

query = 'violity Колгосп тварин'
for inst in instances:
    url = f"{inst}/search?q={urllib.parse.quote(query)}&format=json"
    print(f"Querying {inst}...")
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        print("Status:", res.status_code)
        if res.status_code == 200:
            data = res.json()
            results = data.get('results', [])
            print(f"Found {len(results)} results!")
            for r in results[:3]:
                print(r.get('title'), "->", r.get('url'))
            break
    except Exception as e:
        print("Error:", e)
