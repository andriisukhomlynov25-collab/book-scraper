import sys
import os
import gspread
from google.oauth2.service_account import Credentials

BASE_DIR = os.path.dirname(os.path.abspath('.venv/stealth_scraper_ai.py'))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

print([ws.title for ws in spreadsheet.worksheets()])
