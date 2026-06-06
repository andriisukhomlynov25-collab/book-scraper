import sys

file_path = '.venv/stealth_scraper_ai.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add argument
old_arg = 'parser.add_argument("--headless", action="store_true", help="Run browsers in headless (text) mode")'
new_arg = old_arg + '\n    parser.add_argument("--sheet-name", type=str, default="Палета 1 - Іноземні", help="Name of the worksheet")'
content = content.replace(old_arg, new_arg)

# Change hardcoded worksheet
old_ws = 'worksheet = spreadsheet.worksheet("Палета 1 - Іноземні")'
new_ws = 'worksheet = spreadsheet.worksheet(args.sheet_name)'
# Wait! init_google_clients() doesn't have access to args!
# Let's pass sheet_name to init_google_clients.

old_init = "def init_google_clients():"
new_init = 'def init_google_clients(sheet_name="Палета 1 - Іноземні"):'
content = content.replace(old_init, new_init)

old_ws2 = 'worksheet = spreadsheet.worksheet("Палета 1 - Іноземні")'
new_ws2 = 'worksheet = spreadsheet.worksheet(sheet_name)'
content = content.replace(old_ws2, new_ws2)

# Fix init_google_clients calls
content = content.replace('init_google_clients()', 'init_google_clients(args.sheet_name if "args" in globals() or "args" in locals() else "Палета 1 - Іноземні")')
# Wait, inside main(), we have `args = parser.parse_args()`. We can just change `init_google_clients()` to `init_google_clients(args.sheet_name)`.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
