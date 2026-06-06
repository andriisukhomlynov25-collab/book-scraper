import sys
import pprint
from test_api import authenticate_google_sheets

service = authenticate_google_sheets()
if not service:
    print("Failed to auth")
    sys.exit(1)

SPREADSHEET_ID = '1Zz98y4eT9W91KxX8k_kUv5x0h4-xTWeoU-2h6gB1kMw'
RANGE_NAME = "'Палета 2 - Іноземні'!A1:H20"

try:
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    for idx, row in enumerate(values):
        print(f"Row {idx+1}: {row}")
except Exception as e:
    print(f"Error: {e}")
