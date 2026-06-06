import sys

file_path = '.venv/web_scraper_server.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_prompt = 'Поверни прямі URL на сторінки товарів.'
new_prompt = 'ВАЖЛИВО: Виводь посилання ПОВНІСТЮ (починаючи з https://), ЯК ЗВИЧАЙНИЙ ТЕКСТ, а не як приховані гіперпосилання.'

content = content.replace(old_prompt, new_prompt)

# Also fix extract_urls to handle None
old_extract = """def extract_urls(text):
    urls = re.findall(r'https?://[^\\s<>"]+|www\\.[^\\s<>"]+', text)"""
new_extract = """def extract_urls(text):
    if not text: return []
    urls = re.findall(r'https?://[^\\s<>"]+|www\\.[^\\s<>"]+', text)"""

content = content.replace(old_extract, new_extract)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
