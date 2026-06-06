import os

md_file = "successful_searches.md"
if os.path.exists(md_file):
    print("Reading successful_searches.md...")
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    surrogates = []
    for idx, c in enumerate(content):
        code = ord(c)
        if 0xD800 <= code <= 0xDFFF:
            surrogates.append((idx, c, hex(code)))
    
    if surrogates:
        print(f"Found {len(surrogates)} surrogate characters in successful_searches.md:")
        for idx, c, h in surrogates:
            print(f"  Pos {idx}: character code {h}")
    else:
        print("No surrogate characters found in successful_searches.md!")
else:
    print("File not found!")
