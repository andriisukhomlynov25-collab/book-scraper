import os
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'
SHEET_NAME = 'Палета 1 - Кирилиця'
SERVICE_ACCOUNT_FILE = '/Users/getapp/PycharmProjects/book_scraper/credentials.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet = spreadsheet.worksheet(SHEET_NAME)

all_values = worksheet.get_all_values()
print(f"Total rows in sheet: {len(all_values)}")

for idx, row in enumerate(all_values[:50]):
    row_num = idx + 1
    # print row number and columns A, B, C, D, E, F, G, H
    # fill with empty strings if the row is short
    row_padded = row + [""] * (8 - len(row))
    print(f"Row {row_num:02d}: A={row_padded[0]:<5} | B={row_padded[1]:<5} | C={row_padded[2][:40]:<40} | D={row_padded[3]:<5} | E={row_padded[4]:<5} | F={row_padded[5]:<10} | G={row_padded[6]:<10} | H={row_padded[7]:<10}")
