import re

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
            
    title_part = re.split(r'\s+-\s+|\s+—\s+', title_part)[0]
    title_part = re.sub(r'ISBN[\s\S]*', '', title_part, flags=re.IGNORECASE)
    title_part = re.sub(r'\b\d{4}(?:[–-]\d{4})?\s*г?\.?\b', '', title_part)
    title_part = re.sub(r'\b[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ]\.\s*', '', title_part)
    title_part = re.compile(r'[^\w\s\']', re.UNICODE).sub(' ', title_part)
    
    noise = ['new york', 'london', 'kyiv', 'київ', 'москва', 'moscow', 'spb', 'спб', 'edition', 'vol', 'том', 'paris', 'germany']
    for n in noise:
        title_part = re.compile(r'\b' + re.escape(n) + r'\b', re.IGNORECASE).sub('', title_part)
        
    title_part = ' '.join(title_part.split()).strip()
    author = re.sub(r'[^a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\s\.\-]', ' ', author)
    author = ' '.join(author.split()).strip()
    return author, title_part

def extract_core_title(raw_title):
    author, title = parse_author_and_title(raw_title)
    return f"{author} {title}".strip()
