import requests
import re

url = "https://violity.com/ru/113903127-b-krupnickij-teoriya-rimu-i-shlyahi-rosijskoyi-istoriografiyi-myunhen-1952-diaspora"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
res = requests.get(url, headers=headers)
html = res.text

print(f"Loaded HTML length: {len(html)}")

# Find all occurrences of "250" or "грн"
matches = [m.start() for m in re.finditer(r"250\s*(?:грн|₴)", html)]
print(f"Found {len(matches)} matches for '250 грн'")
for idx, pos in enumerate(matches):
    start = max(0, pos - 150)
    end = min(len(html), pos + 150)
    print(f"\n--- Match {idx+1} (position {pos}) ---")
    print(html[start:end])

# If no exact 250 грн matches, search for "250" alone
if len(matches) == 0:
    matches_250 = [m.start() for m in re.finditer(r"250", html)]
    print(f"Found {len(matches_250)} matches for '250'")
    for idx, pos in enumerate(matches_250[:5]):
        start = max(0, pos - 100)
        end = min(len(html), pos + 100)
        print(f"\n--- 250 Match {idx+1} (position {pos}) ---")
        print(html[start:end])
