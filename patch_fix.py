import re

with open('fix_main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace extract_core_title string in fix_main.py
pattern = r"    \"def extract_core_title\(raw_title\):\\n\".*?    \"    return \\\" \\\".join\(core\.split\(\)\)\.strip\(\)\\n\""
new_extract = """    "def parse_author_and_title(raw_title, existing_author=''):\\n"
    "    if not raw_title: return '', ''\\n"
    "    author = existing_author\\n"
    "    title_part = raw_title\\n"
    "    \\n"
    "    if ' / ' in raw_title:\\n"
    "        parts = raw_title.split(' / ')\\n"
    "        if len(parts) == 2:\\n"
    "            left, right = parts[0], parts[1]\\n"
    "            if len(left.split()) <= 4 and len(right.split()) > 3:\\n"
    "                author = left\\n"
    "                title_part = right\\n"
    "            else:\\n"
    "                title_part = left\\n"
    "                author = right.split(' — ')[0].split(' - ')[0]\\n"
    "    \\n"
    "    if not author and '.' in title_part:\\n"
    "        first_part = title_part.split('.')[0]\\n"
    "        if len(first_part.split()) <= 3:\\n"
    "            author = first_part\\n"
    "            title_part = title_part[len(first_part)+1:]\\n"
    "            \\n"
    "    title_part = re.split(r'\\\\s+-\\\\s+|\\\\s+—\\\\s+', title_part)[0]\\n"
    "    title_part = re.sub(r'ISBN[\\\\s\\\\S]*', '', title_part, flags=re.IGNORECASE)\\n"
    "    title_part = re.sub(r'\\\\b\\\\d{4}(?:[–-]\\\\d{4})?\\\\s*г?\\\\.?\\\\b', '', title_part)\\n"
    "    title_part = re.sub(r'\\\\b[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ]\\\\.\\\\s*', '', title_part)\\n"
    "    title_part = re.compile(r'[^\\\\w\\\\s\\\\\\']', re.UNICODE).sub(' ', title_part)\\n"
    "    \\n"
    "    noise = ['new york', 'london', 'kyiv', 'київ', 'москва', 'moscow', 'spb', 'спб', 'edition', 'vol', 'том', 'paris', 'germany']\\n"
    "    for n in noise:\\n"
    "        title_part = re.compile(r'\\\\b' + re.escape(n) + r'\\\\b', re.IGNORECASE).sub('', title_part)\\n"
    "        \\n"
    "    title_part = ' '.join(title_part.split()).strip()\\n"
    "    author = re.sub(r'[^a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\\\\s\\\\.\\\\-]', ' ', author)\\n"
    "    author = ' '.join(author.split()).strip()\\n"
    "    return author, title_part\\n"
    "\\n"
    "def extract_core_title(raw_title):\\n"
    "    author, title = parse_author_and_title(raw_title)\\n"
    "    return f\\\"{author} {title}\\\".strip()\\n\""
"""
text = re.sub(pattern, new_extract.strip(), text, flags=re.DOTALL)

with open('fix_main.py', 'w', encoding='utf-8') as f:
    f.write(text)
