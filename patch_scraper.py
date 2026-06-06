import re

with open('.venv/foreign_price_scraper_dual.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_extract = """
def parse_author_and_title(raw_title, existing_author=''):
    if not raw_title: return '', ''
    author = existing_author
    title_part = raw_title
    
    if ' / ' in raw_title:
        parts = raw_title.split(' / ')
        if len(parts) == 2:
            left, right = parts[0], parts[1]
            if len(left.split()) <= 4 and len(right.split()) > 3:
                author = left
                title_part = right
            else:
                title_part = left
                author = right.split(' — ')[0].split(' - ')[0]
    
    if not author and '.' in title_part:
        first_part = title_part.split('.')[0]
        if len(first_part.split()) <= 3:
            author = first_part
            title_part = title_part[len(first_part)+1:]
            
    title_part = re.split(r'\\s+-\\s+|\\s+—\\s+', title_part)[0]
    title_part = re.sub(r'ISBN[\\s\\S]*', '', title_part, flags=re.IGNORECASE)
    title_part = re.sub(r'\\b\\d{4}(?:[–-]\\d{4})?\\s*г?\\.?\\b', '', title_part)
    title_part = re.sub(r'\\b[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ]\\.\\s*', '', title_part)
    title_part = re.compile(r'[^\\w\\s\\\']', re.UNICODE).sub(' ', title_part)
    
    noise = ['new york', 'london', 'kyiv', 'київ', 'москва', 'moscow', 'spb', 'спб', 'edition', 'vol', 'том', 'paris', 'germany']
    for n in noise:
        title_part = re.compile(r'\\b' + re.escape(n) + r'\\b', re.IGNORECASE).sub('', title_part)
        
    title_part = ' '.join(title_part.split()).strip()
    author = re.sub(r'[^a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\\s\\.\\-]', ' ', author)
    author = ' '.join(author.split()).strip()
    return author, title_part

def extract_core_title(raw_title):
    author, title = parse_author_and_title(raw_title)
    return f"{author} {title}".strip()
"""

# Replace extract_core_title
pattern = r"def extract_core_title\(raw_title\):.*?return \" \".join\(core\.split\(\)\)\.strip\(\)\n"
text = re.sub(pattern, new_extract.strip() + "\n", text, flags=re.DOTALL)

# Replace search_ebay
ebay_old = r"""def search_ebay\(driver, book_title, author\):
    try:
        combined = f"\{author\} \{book_title\}" if author else book_title
        core = extract_core_title\(combined\)
        query = " "\.join\(core\.split\(\)\[:5\]\)\.strip\(\)
        log_message\(f"🔎 Пошуковий запит eBay: \{query\}"\)"""

ebay_new = """def search_ebay(driver, book_title, author):
    try:
        a, t = parse_author_and_title(book_title, author)
        query = f"{a} {t}"
        query = " ".join(query.split()[:6]).strip()
        log_message(f"🔎 Пошуковий запит eBay: {query}")"""

text = re.sub(ebay_old, ebay_new, text)

# Replace search_amazon
amazon_old = r"""def search_amazon\(driver, book_title, author\):
    try:
        combined = f"\{author\} \{book_title\}" if author else book_title
        core = extract_core_title\(combined\)
        query = " "\.join\(core\.split\(\)\[:6\]\)
        log_message\(f"🔎 Пошуковий запит Amazon: \{query\}"\)"""

amazon_new = """def search_amazon(driver, book_title, author):
    try:
        a, t = parse_author_and_title(book_title, author)
        query = f"{a} {t}"
        query = " ".join(query.split()[:6]).strip()
        log_message(f"🔎 Пошуковий запит Amazon: {query}")"""

text = re.sub(amazon_old, amazon_new, text)

# Replace search_abebooks
abebooks_old = r"""def search_abebooks\(driver, book_title, author\):
    try:
        combined = f"\{author\} \{book_title\}" if author else book_title
        parts = combined\.split\('\. '\)
        if len\(parts\) >= 2:
            author_raw = parts\[0\]
            if ',' in author_raw: ln, fn = author_raw\.split\(',', 1\); author = f"\{fn\.strip\(\)\} \{ln\.strip\(\)\}"\.strip\(\)
            else: author = author_raw\.strip\(\)
            title_part = parts\[1\]\.split\(' : '\)\[0\]\.split\(' — '\)\[0\]\.strip\(\)
            query_str = f"an=\{urllib\.parse\.quote\(author\)\}&tn=\{urllib\.parse\.quote\(title_part\)\}"
        else:
            core = combined\.split\('/'\)\[0\]
            title_part = re\.split\(r' : \| — \| - ', core\)\[0\]\.strip\(\)
            query_str = f"tn=\{urllib\.parse\.quote\(title_part\)\}"
            
        log_message\(f"🔎 Пошуковий запит AbeBooks: \{query_str\}"\)"""

abebooks_new = """def search_abebooks(driver, book_title, author):
    try:
        a, t = parse_author_and_title(book_title, author)
        query_str = f"an={urllib.parse.quote(a)}&tn={urllib.parse.quote(t)}"
        log_message(f"🔎 Пошуковий запит AbeBooks: {query_str}")"""

text = re.sub(abebooks_old, abebooks_new, text)

# Replace search_biblio
biblio_old = r"""def search_biblio\(driver, book_title, author\):
    try:
        combined = f"\{author\} \{book_title\}" if author else book_title
        core = extract_core_title\(combined\)
        title_query = " "\.join\(core\.split\(\)\[:5\]\)
        log_message\(f"🔎 Пошуковий запит Biblio: \{title_query\}"\)
        
        search_url = f"https://www\.biblio\.com/search\.php\?stage=1&title=\{urllib\.parse\.quote\(title_query\)\}"
        driver\.get\(search_url\)"""

biblio_new = """def search_biblio(driver, book_title, author):
    try:
        a, t = parse_author_and_title(book_title, author)
        log_message(f"🔎 Пошуковий запит Biblio: Автор='{a}', Назва='{t}'")
        search_url = f"https://www.biblio.com/search.php?stage=1&author={urllib.parse.quote(a)}&title={urllib.parse.quote(t)}"
        driver.get(search_url)"""

text = re.sub(biblio_old, biblio_new, text)

with open('.venv/foreign_price_scraper_dual.py', 'w', encoding='utf-8') as f:
    f.write(text)

import ast
try:
    ast.parse(text)
    print("Syntax OK")
except Exception as e:
    print("Error:", e)
