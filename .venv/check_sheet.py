import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = '1F1KctUExEnsh9uZpLxcID6HgY1gxkv5fiuvXGMOYw5s'
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
client = gspread.authorize(creds)
ss = client.open_by_key(SPREADSHEET_ID)
ws = ss.sheet1
print(f"Sheet Title: {ws.title}")
records = ws.get_all_values()
print(f"Total rows: {len(records)}")
if len(records) > 1:
    print(f"First data row: {records[1]}")
