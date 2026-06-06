from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

SPREADSHEET_ID = '1KkQe7q7xXQ31vU9L1Cg6xY9q5p9b2fL2fC2z5p8q6h0' # Wait, I need the actual ID
