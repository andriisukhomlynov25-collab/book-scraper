import sys

file_path = '.venv/stealth_scraper_ai.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add global variable at the top
if "CURRENT_SHEET_NAME = " not in content:
    content = content.replace("SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'",
                              "SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'\nCURRENT_SHEET_NAME = 'Палета 1 - Іноземні'")

# Inside main(), set the global variable
old_main = 'args = parser.parse_args()\n\n    # Enforce UTF-8'
new_main = 'args = parser.parse_args()\n    global CURRENT_SHEET_NAME\n    CURRENT_SHEET_NAME = args.sheet_name\n\n    # Enforce UTF-8'
content = content.replace(old_main, new_main)

# Replace the messy init_google_clients calls with CURRENT_SHEET_NAME
content = content.replace('init_google_clients(args.sheet_name if "args" in globals() or "args" in locals() else "Палета 1 - Іноземні")', 'init_google_clients(CURRENT_SHEET_NAME)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
