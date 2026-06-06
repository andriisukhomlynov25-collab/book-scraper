import sys

file_path = '.venv/web_scraper_server.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the log_message to capture stdout
old_log = """def log_message(msg):
    now = time.strftime("%H:%M:%S")
    full_msg = f"[{now}] {msg}"
    print(full_msg)
    logs.append(full_msg)
    if len(logs) > 50:
        logs.pop(0)"""

new_log = """def log_message(msg):
    now = time.strftime("%H:%M:%S")
    full_msg = f"[{now}] {msg}"
    print(full_msg)
    logs.append(full_msg)
    if len(logs) > 100:
        logs.pop(0)

class StdoutRedirector:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
    def write(self, text):
        self.original_stdout.write(text)
        text = text.strip()
        if text:
            now = time.strftime("%H:%M:%S")
            logs.append(f"[{now}] {text}")
            if len(logs) > 100:
                logs.pop(0)
    def flush(self):
        self.original_stdout.flush()

import sys
sys.stdout = StdoutRedirector(sys.stdout)
"""

if "StdoutRedirector" not in content:
    content = content.replace(old_log, new_log)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

