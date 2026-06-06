import sys

with open('.venv/two_button_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "            # STEP-BY-STEP: confirmation BEFORE search"
end_marker = "                try:\n                    worksheet.batch_update(updates"

new_block = """
            print(f"\\n==================================================")
            print(f"📘 РЯДОК {i}")
            print(f"   Книга : {title}")
            print(f"   Рік   : {col_d}")
            print(f"==================================================")
            print("Оберіть дію:")
            print(" [ 1 ] - Відправити запит до ChatGPT (OpenAI API)")
            print(" [ s ] - Пропустити цю книгу")
            print(" [ q ] - Вийти")
            
            user_input = input(">> ").strip().lower()
            if user_input == "q":
                log_message("👋 Вихід за командою користувача.")
                break
            elif user_input == "s":
                log_message(f"⏩ Рядок {i}: Пропущено за командою користувача.")
                skipped_count += 1
                continue
            elif user_input != "1":
                log_message("Невідома команда. Пропускаємо рядок.")
                continue

            matches = []
            ai_links = get_links_from_openai(title, col_d)
            
            if not ai_links:
                log_message("⚠️ OpenAI не повернув посилань. Переходимо до наступної книги.")
                continue
                
            print(f"\\n✅ ChatGPT повернув {len(ai_links)} посилань:")
            for link_info in ai_links:
                print(f"   🔗 {link_info['site']}: {link_info['url'][:80]}")
                
            print("\\nОберіть дію:")
            print(" [ 2 ] - Перейти за посиланнями, зібрати ціни та зберегти")
            print(" [ 3 ] (або s) - Пропустити (посилання не підходять)")
            print(" [ q ] - Вийти")
            
            action2 = input(">> ").strip().lower()
            if action2 == "q":
                log_message("👋 Вихід за командою користувача.")
                break
            elif action2 in ["3", "s"]:
                log_message(f"⏩ Рядок {i}: Пропущено за командою користувача (посилання відхилено).")
                skipped_count += 1
                continue
            elif action2 != "2":
                log_message("Невідома команда. Пропускаємо рядок.")
                continue
                
            # Execute step 2
            for link_info in ai_links:
                if len(matches) >= len(empty_cols):
                    break
                    
                site = link_info['site']
                url = link_info['url']
                log_message(f"🔍 Перевірка посилання від OpenAI ({site}): {url[:80]}...")
                
                try:
                    col_char = col_chars[empty_cols[len(matches)]]
                    formula, price = process_product_page(driver_store, url, site, i, col_char, title)
                    if formula:
                        matches.append({'site': site, 'price': price, 'formula': formula, 'url': url})
                        log_message(f"✅ Знайдено ціну на {site}: {price}")
                    else:
                        log_message(f"❌ Посилання не пройшло перевірку або не містить ціни.")
                except Exception as err:
                    log_message(f"⚠️ Помилка обробки посилання {url}: {err}")

            if matches:
                updates = []
                notes_to_update = []
                for idx, match in enumerate(matches):
                    target_c_idx = empty_cols[idx]
                    char = col_chars[target_c_idx]
                    updates.append({'range': f"{char}{i}", 'values': [[match['formula']]]})
                    notes_to_update.append((char, match['url']))

"""

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_block + content[end_idx:]
    with open('.venv/two_button_scraper.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Patched successfully")
else:
    print(f"Could not find markers. Start: {start_idx}, End: {end_idx}")

