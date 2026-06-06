import os
import re
from datetime import datetime

md_file = "successful_searches.md"
existing_matches = []
if os.path.exists(md_file):
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        table_started = False
        for line in lines:
            if "| Row" in line or "|---" in line:
                table_started = True
                continue
            if table_started and line.strip().startswith("|"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 6:
                    try:
                        clean_row = parts[0].replace("**", "").strip()
                        r = int(clean_row)
                        t = parts[1].replace("\\|", "|").strip()
                        s = parts[2].replace("`", "").strip()
                        p = parts[3].replace("`", "").strip()
                        u_match = re.search(r'\[Link\]\((.*?)\)', parts[5])
                        u = u_match.group(1) if u_match else parts[5].strip()
                        d = parts[6].strip()
                        existing_matches.append({
                            'row': r, 'title': t, 'site': s, 'price': p, 'url': u, 'date': d
                        })
                        print(f"Parsed Row {r}: {t[:20]} | {s} | {p}")
                    except Exception as err:
                        print(f"Error parsing line: {line.strip()} - {err}")
    except Exception as e:
        print(f"Error reading file: {e}")

# Try to re-write
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
total_found = len(set(x['row'] for x in existing_matches))
site_counts = {}
for ex in existing_matches:
    site_counts[ex['site']] = site_counts.get(ex['site'], 0) + 1

ebay_count = site_counts.get('ebay.com', 0)
amazon_count = site_counts.get('amazon.com', 0)
abebooks_count = site_counts.get('abebooks.com', 0)
biblio_count = site_counts.get('biblio.com', 0)

try:
    with open("test_output.md", "w", encoding="utf-8") as f:
        f.write("# \U0001f4da Autonomous Book Scraper - Live Report\n\n")
        f.write("> [!NOTE]\n")
        f.write("> This report is updated in **real-time** by the autonomous scraper. It aggregates results from all runs to show a complete history of found book prices.\n\n")
        f.write("## \U0001f4ca Scraper Session Dashboard\n")
        f.write(f"- **Last Updated:** `{now_str}`\n")
        f.write(f"- **Total Unique Books Found:** `{total_found}`\n")
        f.write("- **Site Match Distribution:**\n")
        f.write(f"  - \U0001f6cd\ufe0f **eBay:** `{ebay_count}` matches\n")
        f.write(f"  - \U0001f4e6 **Amazon:** `{amazon_count}` matches\n")
        f.write(f"  - \U0001f4d6 **AbeBooks:** `{abebooks_count}` matches\n")
        f.write(f"  - \U0001f4da **Biblio:** `{biblio_count}` matches\n\n")
        f.write("---\n\n")
        f.write("## \U0001f4c8 Search Success History\n")
        f.write("| Row | Title | Site | Original Price | Formula | Source Link | Found At |\n")
        f.write("|:---:|---|:---:|:---:|:---:|:---:|:---:|\n")
        for ex in existing_matches:
            clean_t = ex['title'].replace("|", "\\|")
            pr = ex['price']
            if not pr.startswith("$") and not pr.startswith("\u20ac") and not pr.startswith("\u00a3"):
                if pr and (pr[0].isdigit() or pr[0] == '.'):
                    pr = f"${pr}"
            raw_numeric = re.sub(r'[^\d.]', '', ex['price'])
            formula = f"`={raw_numeric}*CURRENCY`" if raw_numeric else "N/A"
            f.write(f"| **{ex['row']}** | {clean_t} | `{ex['site']}` | `{pr}` | {formula} | [Link]({ex['url']}) | {ex['date']} |\n")
    print("Write test successful!")
except Exception as e:
    print(f"Write test failed: {e}")
