import requests
import re
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
res = requests.get('https://www.bing.com/search?q=orwell', headers=headers)
print("Title:", getattr(re.search(r'<title>(.*?)</title>', res.text), 'group', lambda x: None)(1))
print("Contains b_results:", 'b_results' in res.text)
print("Contains b_algo:", 'b_algo' in res.text)
print("Length:", len(res.text))
