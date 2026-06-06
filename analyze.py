import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'
RANGE_NAME = 'Палета 1 - Іноземні!A1:H1000'

def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    
    missing_all = []
    has_some = []
    
    for i, row in enumerate(values):
        if i == 0: continue # skip header
        
        # Cols F, G, H correspond to index 5, 6, 7
        f = row[5] if len(row) > 5 else ''
        g = row[6] if len(row) > 6 else ''
        h = row[7] if len(row) > 7 else ''
        
        if f.strip() == '' and g.strip() == '' and h.strip() == '':
            missing_all.append(i + 1) # row number
        else:
            has_some.append(i + 1)
            
    print(f"Total rows (excl header): {len(values) - 1}")
    print(f"Rows with SOME price: {len(has_some)}")
    print(f"Rows missing ALL prices: {len(missing_all)}")
    print(f"First 20 missing: {missing_all[:20]}")

if __name__ == '__main__':
    main()
