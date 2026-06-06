import os
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
sheet_client = gspread.authorize(creds)
spreadsheet = sheet_client.open_by_key(SPREADSHEET_ID)

print("Worksheets available:")
for w in spreadsheet.worksheets():
    print(f"- {w.title}")
