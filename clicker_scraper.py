import sys
import os
import re
import time
import subprocess
import urllib.parse
import threading
import gspread
import webbrowser
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pyperclip
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller

# ================= КОНФІГУРАЦІЯ =================
SPREADSHEET_ID = '18EnQg_RaaHQPyUuAmO_S1ft9KAXEyJ2M8DjxE6URWO8'
SHARED_DRIVE_FOLDER_ID = '0AHvgRKQpv3qrUk9PVA'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

sheet_client = None
drive_service = None
spreadsheet = None
worksheet = None

# Глобальні змінні стану
current_row = 2
current_title = ""
current_year = ""
current_row_data = []
all_data_len = 0
is_processing = False
last_key_time = 0
hotkeys_enabled = True

kb_controller = Controller()

def log_message(msg):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"\033[90m[{now}]\033[0m {msg}")

def play_success_sound():
    try:
        # Безшумно граємо системний звук успіху на macOS
        sound_path = "/System/Library/Sounds/Glass.aiff"
        if os.path.exists(sound_path):
            subprocess.Popen(["afplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def play_error_sound():
    try:
        sound_path = "/System/Library/Sounds/Basso.aiff"
        if os.path.exists(sound_path):
            subprocess.Popen(["afplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def get_frontmost_app():
    try:
        cmd = "osascript -e 'tell application \"System Events\" to name of first application process whose frontmost is true'"
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, shell=True).decode('utf-8').strip()
    except:
        return ""

def is_browser_active():
    app = get_frontmost_app().lower()
    browsers = ["chrome", "safari", "brave", "arc", "opera", "firefox", "vivaldi", "edge"]
    return any(b in app for b in browsers)

def get_active_browser_url():
    front_app = get_frontmost_app()
    front_app_lower = front_app.lower()
    
    # Перевіряємо, чи активний додаток є одним із підтримуваних браузерів
    is_chromium = any(b in front_app_lower for b in ["chrome", "brave", "arc", "opera", "edge", "vivaldi"])
    is_safari = "safari" in front_app_lower
    
    if is_chromium:
        try:
            cmd = f"osascript -e 'tell application \"{front_app}\" to get URL of active tab of first window'"
            url = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, shell=True).decode('utf-8').strip()
            if url.startswith("http"):
                return url, front_app
        except:
            pass
            
    if is_safari or front_app_lower == "":
        try:
            cmd = "osascript -e 'tell application \"Safari\" to get URL of document 1'"
            url = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, shell=True).decode('utf-8').strip()
            if url.startswith("http"):
                return url, "Safari"
        except:
            pass
            
    # Резервний перебір
    for browser in ["Google Chrome", "Brave Browser", "Arc", "Safari", "Microsoft Edge", "Opera"]:
        try:
            if "safari" in browser.lower():
                cmd = "osascript -e 'tell application \"Safari\" to get URL of document 1'"
            else:
                cmd = f"osascript -e 'tell application \"{browser}\" to get URL of active tab of first window'"
            url = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, shell=True).decode('utf-8').strip()
            if url.startswith("http"):
                return url, browser
        except:
            pass
            
    return "", ""

def init_google_clients():
    global sheet_client, drive_service, spreadsheet
    log_message("🔌 Підключення до Google API...")
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
        sheet_client = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds, cache_discovery=False)
        spreadsheet = sheet_client.open_by_key(SPREADSHEET_ID)
        log_message("✅ Google API підключено успішно.")
    except Exception as e:
        log_message(f"❌ Помилка підключення Google API: {e}")
        play_error_sound()
        sys.exit(1)

def print_book_banner():
    global current_row, current_title, current_year, current_row_data, worksheet
    os.system('clear')
    print("\033[95m======================================================================\033[0m")
    print(f"\033[1;97m📘 РЯДОК {current_row} \033[0m | Аркуш: \033[93m{worksheet.title}\033[0m")
    print(f"\033[1;92m   Книга: {current_title}\033[0m")
    print(f"\033[1;96m   Рік:   {current_year}\033[0m")
    print("\033[95m======================================================================\033[0m")
    
    # Виводимо статус цін
    col_f = current_row_data[5].strip() if len(current_row_data) > 5 else ""
    col_g = current_row_data[6].strip() if len(current_row_data) > 6 else ""
    col_h = current_row_data[7].strip() if len(current_row_data) > 7 else ""
    
    def format_price_status(val):
        if not val:
            return "\033[91mпорожньо\033[0m"
        # Спрощуємо виведення формули для гарного вигляду
        if "HYPERLINK" in val:
            match = re.search(r'HYPERLINK\("[^"]+";\s*"([^"]+)"\)', val)
            if match:
                return f"\033[92m{match.group(1)} (із скріншотом)\033[0m"
        return f"\033[92m{val}\033[0m"
        
    print(f"   [F] Ціна 1 : {format_price_status(col_f)}")
    print(f"   [G] Ціна 2 : {format_price_status(col_g)}")
    print(f"   [H] Ціна 3 : {format_price_status(col_h)}")
    print("\033[95m----------------------------------------------------------------------\033[0m")
    print("⌨️  \033[1;97mГЛОБАЛЬНІ ГАРЯЧІ КЛАВІШІ (працюють у Chrome або Safari):\033[0m")
    print("   • \033[1;93mКнопка [ 1 ]\033[0m — Наступна книга (Row + 1) та автоматичний пошук")
    print("   • \033[1;93mКнопка [ 2 ]\033[0m — Попередня книга (Row - 1)")
    print("   • \033[1;93mКнопка [ 3 ]\033[0m — Скопіювати назву поточної книги в буфер")
    print("   • \033[1;92mПодвійний клік на ціну\033[0m — Зберегти ціну, посилання та скріншот")
    print("\033[95m----------------------------------------------------------------------\033[0m")
    state_str = "\033[1;92mУВІМКНЕНО\033[0m" if hotkeys_enabled else "\033[1;91mВИМКНЕНО (пауза)\033[0m"
    print(f"ℹ️ Стан гарячих клавіш: {state_str} (натисніть [ F8 ] для перемикання)")
    print("ℹ️ Введіть \033[1;93mq\033[0m у терміналі для безпечного виходу")
    print("\033[95m======================================================================\033[0m")

def open_google_search():
    global current_title, current_year
    if current_title and current_title != "Невідома назва":
        search_query = urllib.parse.quote(f"{current_title} {current_year}".strip())
        url = f"https://www.google.com/search?q={search_query}"
        log_message(f"🌐 Відкриваємо пошук у браузері...")
        try:
            # Спеціально відкриваємо Google Chrome на macOS
            subprocess.Popen(["open", "-a", "Google Chrome", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            try:
                webbrowser.open(url)
            except Exception as e:
                log_message(f"❌ Не вдалося відкрити браузер: {e}")

def load_row(row_idx):
    global current_row, current_title, current_year, current_row_data, worksheet, all_data_len
    
    current_row = row_idx
    for attempt in range(3):
        try:
            # Завантажуємо свіжі дані рядка
            current_row_data = worksheet.row_values(row_idx)
            
            # Назва книги знаходиться в стовпчику C (індекс 2)
            if len(current_row_data) >= 3:
                current_title = current_row_data[2].strip()
            else:
                current_title = "Невідома назва"
                
            # Рік знаходиться в стовпчику D (індекс 3)
            if len(current_row_data) >= 4:
                current_year = current_row_data[3].strip()
            else:
                current_year = ""
                
            print_book_banner()
            # Копіюємо назву книги в буфер обміну автоматично
            try:
                pyperclip.copy(current_title)
                log_message("📋 Назву книги автоматично скопійовано в буфер!")
            except Exception as e:
                log_message(f"⚠️ Не вдалося автоматично скопіювати в буфер: {e}")
            return True
        except Exception as e:
            log_message(f"⚠️ [Спроба {attempt+1}] Помилка завантаження рядка {row_idx}: {e}")
            time.sleep(1)
    
    log_message("❌ Не вдалося завантажити рядок після кількох спроб.")
    play_error_sound()
    return False

def next_row():
    global current_row, all_data_len
    if current_row < 5000: # Обмеження зверху для безпеки
        success = load_row(current_row + 1)
        if success:
            open_google_search()

def prev_row():
    global current_row
    if current_row > 2:
        load_row(current_row - 1)

def trigger_double_click_capture():
    global current_row, worksheet, drive_service, is_processing
    if is_processing:
        return
    is_processing = True
    
    try:
        url, browser = get_active_browser_url()
        if not url:
            is_processing = False
            return
            
        log_message(f"🎯 Виявлено подвійний клік у {browser}! Зчитуємо ціну...")
        
        # Симулюємо Cmd+C
        # Очищуємо буфер перед копіюванням для надійності
        pyperclip.copy("")
        
        kb_controller.press(Key.cmd)
        kb_controller.press('c')
        time.sleep(0.05)
        kb_controller.release('c')
        kb_controller.release(Key.cmd)
        time.sleep(0.3) # Даємо час системі заповнити буфер обміну
        
        price = pyperclip.paste().strip()
        if not price:
            log_message("⚠️ Буфер обміну порожній. Переконайтеся, що виділено текст ціни.")
            play_error_sound()
            is_processing = False
            return
            
        log_message(f"💰 Отримано ціну з буфера: \"{price}\"")
        
        # Визначаємо перший порожній стовпчик (F, G, H)
        # Отримуємо найсвіжіші дані рядка безпосередньо перед записом
        row_data = worksheet.row_values(current_row)
        
        col_indices = [5, 6, 7] # F, G, H
        col_chars = {5: 'F', 6: 'G', 7: 'H'}
        col_char = None
        
        for c_idx in col_indices:
            val = row_data[c_idx].strip() if len(row_data) > c_idx else ""
            if not val:
                col_char = col_chars[c_idx]
                break
                
        if not col_char:
            log_message("⚠️ Всі 3 ціни (F, G, H) вже заповнені для цієї книги! Пропускаємо.")
            play_error_sound()
            is_processing = False
            return
            
        log_message(f"📸 Робимо скріншот та завантажуємо в стовпчик {col_char}...")
        
        # Створюємо скріншот
        os.makedirs(os.path.join(BASE_DIR, "screenshots"), exist_ok=True)
        scr_name = f"proof_{current_row}_{col_char}.png"
        scr_path = os.path.join(BASE_DIR, "screenshots", scr_name)
        
        subprocess.run(f"screencapture -x {scr_path}", shell=True)
        
        if not os.path.exists(scr_path):
            log_message("❌ Помилка: Не вдалося створити скріншот.")
            play_error_sound()
            is_processing = False
            return
            
        log_message("☁️  Завантажуємо скріншот на Google Drive...")
        
        # Завантажуємо на Google Drive
        file_metadata = {'name': scr_name, 'parents': [SHARED_DRIVE_FOLDER_ID]}
        media = MediaFileUpload(scr_path, mimetype='image/png')
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        file_id = file.get('id')
        
        # Робимо файл доступним для всіх за посиланням
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            supportsAllDrives=True
        ).execute()
        
        scr_link = f"https://drive.google.com/uc?export=view&id={file_id}"
        
        # Записуємо формулу
        formula = f'=HYPERLINK("{scr_link}"; "{price}")'
        
        log_message(f"📝 Оновлюємо комірку {col_char}{current_row}...")
        worksheet.update(values=[[formula]], range_name=f"{col_char}{current_row}", value_input_option='USER_ENTERED')
        
        # Додаємо джерело у примітку
        try:
            worksheet.update_note(f"{col_char}{current_row}", f"Джерело: {url}")
        except Exception as e:
            log_message(f"⚠️ Не вдалося додати примітку джерела: {e}")
            
        log_message(f"🎉 Успішно записано {price} в {col_char}{current_row}!")
        play_success_sound()
        
        # Оновлюємо відображення
        load_row(current_row)
        
        # Видаляємо локальний скріншот після успішного завантаження
        if os.path.exists(scr_path):
            os.remove(scr_path)
            
    except Exception as e:
        log_message(f"❌ Сталася помилка під час обробки подвійного кліку: {e}")
        play_error_sound()
        
    finally:
        is_processing = False

# --- СЛУХАЧІ ПОДІЙ ---

def on_keyboard_press(key):
    global last_key_time, hotkeys_enabled
    
    # F8 служить глобальним перемикачем увімкнення/вимкнення гарячих клавіш
    if key == keyboard.Key.f8:
        hotkeys_enabled = not hotkeys_enabled
        state_str = "УВІМКНЕНО" if hotkeys_enabled else "ВИМКНЕНО (пауза)"
        log_message(f"🔄 Стан гарячих клавіш змінено: {state_str}")
        play_success_sound()
        print_book_banner()
        return

    if not hotkeys_enabled:
        return
        
    # Дозволяємо перемикання гарячих клавіш лише якщо активний браузер
    if not is_browser_active():
        return
        
    now = time.time()
    # Захист від брязкоту контактів клавіатури (cooldown 0.8s)
    if now - last_key_time < 0.8:
        return
        
    try:
        if hasattr(key, 'char') and key.char == '1':
            last_key_time = now
            log_message("1️⃣ Натиснуто кнопка 1 -> Наступний рядок...")
            next_row()
        elif hasattr(key, 'char') and key.char == '2':
            last_key_time = now
            log_message("2️⃣ Натиснуто кнопка 2 -> Попередній рядок...")
            prev_row()
        elif hasattr(key, 'char') and key.char == '3':
            last_key_time = now
            log_message("3️⃣ Натиснуто кнопка 3 -> Копіюємо назву книги в буфер...")
            try:
                pyperclip.copy(current_title)
                play_success_sound()
            except Exception as e:
                log_message(f"❌ Помилка копіювання: {e}")
    except AttributeError:
        pass

# Для мишки детектуємо подвійний клік на ліву кнопку
last_click_time = 0
click_count = 0

def on_mouse_click(x, y, button, pressed):
    global last_click_time, click_count, hotkeys_enabled
    
    if not hotkeys_enabled:
        return
        
    if pressed and button == mouse.Button.left:
        if not is_browser_active():
            return
            
        now = time.time()
        if now - last_click_time < 0.35:
            click_count += 1
        else:
            click_count = 1
        last_click_time = now
        
        if click_count == 2:
            click_count = 0
            # Запускаємо в окремому потоці, щоб не блокувати слухач миші pynput
            t = threading.Thread(target=trigger_double_click_capture)
            t.start()

def main():
    global worksheet, current_row
    
    os.system('clear')
    print("\033[95m======================================================================\033[0m")
    print("🌟 \033[1;97mВІТАЄМО В НАПІВАВТОМАТИЧНОМУ КЛІКЕРНОМУ СКРАПЕРІ!\033[0m 🌟")
    print("\033[95m======================================================================\033[0m")
    
    import argparse
    parser = argparse.ArgumentParser(description="Клікерний Скрапер для Google Таблиць")
    parser.add_argument("-s", "--sheet", type=str, default=None, help="Номер або назва аркуша")
    parser.add_argument("-r", "--row", type=int, default=None, help="Початковий рядок")
    args = parser.parse_args()
    
    init_google_clients()
    
    # Вибираємо аркуш
    try:
        worksheets = spreadsheet.worksheets()
        worksheet = None
        
        # Спроба зчитати аргумент аркуша
        if args.sheet is not None:
            if args.sheet.isdigit():
                idx = int(args.sheet)
                if 1 <= idx <= len(worksheets):
                    worksheet = worksheets[idx - 1]
            else:
                for ws in worksheets:
                    if ws.title.strip().lower() == args.sheet.strip().lower():
                        worksheet = ws
                        break
        
        # Якщо аргумент не передано або він невірний, виводимо інтерактивне меню
        if worksheet is None:
            print("\n📋 Доступні аркуші в Google Таблиці:")
            for idx, ws in enumerate(worksheets):
                print(f"  [\033[92m{idx + 1}\033[0m] {ws.title}")
                
            choice = input("\nОберіть номер аркуша (за замовчуванням 2): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(worksheets):
                worksheet = worksheets[int(choice) - 1]
            else:
                worksheet = worksheets[1] # Дефолт - 'Палета 2 - Іноземні'
                
        log_message(f"Обрано аркуш: {worksheet.title}")
        
        # Визначаємо стартовий рядок
        if args.row is not None:
            start_row = args.row
        else:
            start_row_str = input("Введіть початковий рядок (наприклад, 40): ").strip()
            if start_row_str.isdigit():
                start_row = int(start_row_str)
            else:
                start_row = 40
                
    except Exception as e:
        log_message(f"❌ Помилка ініціалізації аркуша: {e}")
        play_error_sound()
        sys.exit(1)
        
    # Завантажуємо перший обраний рядок
    success = load_row(start_row)
    if not success:
        sys.exit(1)
        
    # Запускаємо слухачі
    has_accessibility = False
    try:
        keyboard_listener = keyboard.Listener(on_press=on_keyboard_press)
        mouse_listener = mouse.Listener(on_click=on_mouse_click)
        
        keyboard_listener.start()
        mouse_listener.start()
        
        log_message("✅ Глобальні фонові слухачі клавіатури та миші активовано.")
        has_accessibility = True
    except Exception as e:
        log_message(f"⚠️  Увага: Не вдалося активувати глобальні гарячі клавіші та кліки.")
        log_message("ℹ️  Причина: Для цього потрібні права Accessibility в macOS.")
        log_message("ℹ️  Скрапер АВТОМАТИЧНО переходить в безвідмовний консольний режим!")
        has_accessibility = False
        play_error_sound()
        
    if has_accessibility:
        # Окремий інтерфейс для безпечного виходу
        while True:
            try:
                cmd = input().strip().lower()
                if cmd == 'q':
                    log_message("👋 Завершення роботи...")
                    play_success_sound()
                    break
            except (KeyboardInterrupt, SystemExit):
                log_message("👋 Завершення роботи...")
                break
                
        keyboard_listener.stop()
        mouse_listener.stop()
    else:
        # Безвідмовний консольний режим (якщо немає прав Універсального доступу)
        print("\n\033[93m⌨️  АКТИВОВАНО КОНСОЛЬНИЙ РЕЖИМ (вводьте команди в терміналі):\033[0m")
        print("   • Введіть \033[1;92m1\033[0m — Наступна книга (Row + 1) та автоматичний пошук")
        print("   • Введіть \033[1;92m2\033[0m — Попередня книга (Row - 1)")
        print("   • Введіть \033[1;92m3\033[0m — Скопіювати назву поточної книги в буфер")
        print("   • Введіть \033[1;92ms\033[0m — Зберегти ціну (зчитає ціну з буфера обміну, зробить скріншот та завантажить!)")
        print("   • Введіть \033[1;91mq\033[0m — Безпечний вихід")
        print("\033[95m======================================================================\033[0m")
        
        while True:
            try:
                cmd = input(f"\n[Рядок {current_row}] Введіть команду (1/2/3/s/q): ").strip().lower()
                if not cmd:
                    continue
                if cmd == '1':
                    log_message("1️⃣ Перехід до наступного рядка...")
                    next_row()
                elif cmd == '2':
                    log_message("2️⃣ Перехід до попереднього рядка...")
                    prev_row()
                elif cmd == '3':
                    log_message("📋 Копіюємо назву книги в буфер...")
                    try:
                        pyperclip.copy(current_title)
                        play_success_sound()
                    except Exception as err:
                        log_message(f"❌ Помилка копіювання: {err}")
                elif cmd == 's':
                    log_message("💾 Збереження ціни та створення скріншоту...")
                    trigger_double_click_capture()
                elif cmd == 'q':
                    log_message("👋 Завершення роботи...")
                    play_success_sound()
                    break
                else:
                    log_message("⚠️  Невідома команда. Спробуйте: 1, 2, 3, s, q")
            except (KeyboardInterrupt, SystemExit):
                log_message("👋 Завершення роботи...")
                break

if __name__ == "__main__":
    main()
