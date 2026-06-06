#!/bin/bash
source .venv/bin/activate
echo "=== Розпочато Палета 1 - Іноземні ==="
python3 .venv/stealth_scraper_ai.py --start-row 472 --sheet-name "Палета 1 - Іноземні"
echo "=== Розпочато Палета 2 - Іноземні ==="
python3 .venv/stealth_scraper_ai.py --start-row 2 --sheet-name "Палета 2 - Іноземні"
echo "=== ВСЕ ГОТОВО ==="
