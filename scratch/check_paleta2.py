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

worksheet = spreadsheet.worksheet("Палета 2 - Іноземні")
all_data = worksheet.get_all_values()
print(f"Total rows in Paleta 2: {len(all_data)}")
print("Headers (Row 1):", all_data[0] if len(all_data) > 0 else "Empty")
print("Row 2:", all_data[1] if len(all_data) > 1 else "Empty")
print("Row 3:", all_data[2] if len(all_data) > 2 else "Empty")
