import os
import gspread
from google.oauth2.service_account import Credentials

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, '../credentials.json')
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

for sheet in spreadsheet.worksheets():
    print(f"\nWorksheet: {sheet.title}")
    rows = sheet.get_all_values()
    if not rows:
        print("Empty")
        continue
    # Let's print first 3 rows, but all columns
    for r_idx, r in enumerate(rows[:5]):
        print(f"  Row {r_idx+1}: {r}")
