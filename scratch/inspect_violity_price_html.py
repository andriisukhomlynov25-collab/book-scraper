import re

# Read the page source from the previous run
# Wait, scratch/inspect_violity_dom.py printed: "Page Source length: 299858 chars"
# But it didn't save the page source to a file!
# Let's write a small script to fetch the Violity URL again and look for "8 000" or "8000" or "грн" in the HTML source using standard requests (since it's a public auction page and doesn't block standard GET requests!)
import requests

url = "https://violity.com/ua/114678091-orvell-kolgosp-tvarin-peredmova-avtora-do-cogo-vidannya-di-pi-1947"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
res = requests.get(url, headers=headers)
html = res.text

print(f"Loaded HTML of length {len(html)}")

# Find all occurrences of "8 000" or "8000" or "грн" in context
# Print 200 characters around each occurrence
matches = [m.start() for m in re.finditer(r"8\s*000", html)]
print(f"Found {len(matches)} matches for '8 000' or '8000'")
for idx, pos in enumerate(matches):
    start = max(0, pos - 150)
    end = min(len(html), pos + 150)
    print(f"\n--- Match {idx+1} (position {pos}) ---")
    print(html[start:end])
