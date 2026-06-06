import requests
import ssl
from urllib3.poolmanager import PoolManager
import urllib.parse
import re

class TLS12Adapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        # Force TLS 1.2 by disabling TLS 1.3
        try:
            context.options |= ssl.OP_NO_TLSv1_3
        except AttributeError:
            pass
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

session = requests.Session()
session.mount('https://', TLS12Adapter())

query = 'site:violity.com Колгосп тварин'
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'

try:
    res = session.get(url, headers=headers)
    print("Status:", res.status_code)
    print("Length:", len(res.text))
    # Print the title to check if we got results page
    title_match = re.search(r'<title>(.*?)</title>', res.text)
    print("Title:", title_match.group(1) if title_match else None)
except Exception as e:
    print("Error:", e)
