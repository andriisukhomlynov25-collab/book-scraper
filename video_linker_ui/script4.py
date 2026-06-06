import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from deep_translator import GoogleTranslator  # Нова бібліотека для перекладу

# --- КОНФІГУРАЦІЯ ---
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/youtube.readonly']
DOCUMENT_ID = '1i7p_O2vGCiwrtvZ6laMq59VWe03H00KeK9R4-7x3Jcs'  # Візьміть з URL документа
YOUTUBE_API_KEY = 'AIzaSyAswYheuDa9qZSexill8upSNtDzmXLULk4'  # Отримайте в Google Cloud Console


def get_creds():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def translate_query(text):
    """Додає уточнення для пошуку візуальних задач на рух"""
    try:
        # Перекладаємо основну тему
        translated = GoogleTranslator(source='uk', target='en').translate(text)

        # Додаємо уточнюючі теги для візуалізації
        visual_tags = " animation motion problems visual simulation"
        final_query = translated + visual_tags

        print(f"🔎 Шукаю: {final_query}")
        return final_query
    except Exception as e:
        return text + " motion problems animation"


def find_youtube_videos(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=5,
        relevanceLanguage='en',
        safeSearch='strict', # Додайте цей рядок для шкільного фільтра
        videoCategoryId='27' # Категорія "Education" на YouTube
    )
    response = request.execute()

    videos = []
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append({'title': video_title, 'url': video_url})
    return videos


def append_to_doc(service, text):
    """Додає текст у кінець документа"""
    # 1. Отримуємо актуальний стан документа, щоб знати його довжину
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    # Останній індекс документа (кінець)
    end_index = doc.get('body').get('content')[-1].get('endIndex') - 1

    # Якщо документ порожній, endIndex може бути менше 1, тому ставимо мінімум 1
    if end_index < 1: end_index = 1

    requests = [
        {
            'insertText': {
                'location': {
                    'index': end_index,
                },
                'text': text + '\n'
            }
        }
    ]
    service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()


def main():
    creds = get_creds()
    docs_service = build('docs', 'v1', credentials=creds)

    for item in multilingual_topics:
        header = f"\n=== ТЕМА: {item['uk']} ===\n"
        append_to_doc(docs_service, header)

        # Список мов для ітерації
        languages = [
            {'name': '🇬🇧 ENGLISH', 'query': item['en'], 'relevance': 'en'},
            {'name': '🇩🇪 GERMANY', 'query': item['de'], 'relevance': 'de'},
            {'name': '🇫🇷 FRANCE', 'query': item['fr'], 'relevance': 'fr'}
        ]

        for lang in languages:
            print(f"🔎 Шукаю {lang['name']} для теми: {item['uk']}")
            # Викликаємо пошук (maxResults=5 вже має бути у функції)
            videos = find_youtube_videos(lang['query'])

            entry = f"\n📍 REGION: {lang['name']}\n"
            for i, v in enumerate(videos, 1):
                entry += f"{i}. {v['title']}\n   🔗 {v['url']}\n"

            append_to_doc(docs_service, entry)


multilingual_topics = [
    {
        "uk": "Задачі на рух",
        "en": "Motion diagram cars animation",
        "de": "Bewegungsaufgaben animation",
        "fr": "Problèmes de mouvement animation"
    }
]


def main():
    # 1. Авторизація (Google Docs та YouTube)
    creds = get_creds()
    docs_service = build('docs', 'v1', credentials=creds)

    # 2. Основний цикл по темах
    for item in multilingual_topics:
        # Додаємо заголовок теми в документ
        header = f"\n📘 ТЕМА: {item['uk'].upper()}\n"
        header += "==========================================\n"
        append_to_doc(docs_service, header)
        print(f"🚀 Починаю пошук для теми: {item['uk']}")

        # 3. Список мов для пошуку (EN, DE, FR)
        languages = [
            {'name': '🇬🇧 ENGLISH', 'query': item['en']},
            {'name': '🇩🇪 GERMANY', 'query': item['de']},
            {'name': '🇫🇷 FRANCE', 'query': item['fr']}
        ]

        for lang in languages:
            print(f"   🔎 Шукаю {lang['name']}...")

            # Викликаємо функцію пошуку YouTube
            video_list = find_youtube_videos(lang['query'])

            if video_list:
                # Формуємо блок тексту для конкретної мови
                entry = f"\n📍 REGION: {lang['name']}\n"
                for i, video in enumerate(video_list, 1):
                    entry += f"{i}. {video['title']}\n   🔗 {video['url']}\n"

                # Записуємо в Google Документ
                append_to_doc(docs_service, entry)
            else:
                print(f"   ⚠️ Відео для {lang['name']} не знайдено.")

        print(f"✅ Тема '{item['uk']}' повністю оброблена та додана в документ.\n")


# Цей блок має бути без відступів взагалі
if __name__ == '__main__':
    main()