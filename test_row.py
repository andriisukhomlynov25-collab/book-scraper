import sys
sys.path.append(".venv")
import foreign_price_scraper_dual as fps

fps.init_google_clients()
data = fps.worksheet.get_all_values()
for i in range(1, 15):
    if i >= len(data): continue
    row = data[i]
    print(f"Row {i+1}: {row}")
