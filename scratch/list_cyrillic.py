import sys
import os
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = '.venv/credentials.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key('18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8').worksheet('Палета 1 - Кирилиця')
    
    rows = sheet.get_all_values()
    print(f"Total rows in sheet: {len(rows)}")
    for idx, r in enumerate(rows[1:30], start=2):
        print(f"Row {idx}: {r[2]} | {r[3]}")
except Exception as e:
    print(f"Error: {e}")
