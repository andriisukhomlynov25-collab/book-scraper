import sys

with open('.venv/hotkey_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('''    try:
        sr = input("З якого рядка почати? (Enter = 2): ").strip()
        current_row = int(sr) if sr.isdigit() else 2
    except:
        current_row = 2''', '''    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-row", type=int, default=2)
    args = parser.parse_args()
    current_row = args.start_row''')

with open('.venv/hotkey_scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)
