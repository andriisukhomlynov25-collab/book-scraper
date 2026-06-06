import sys

with open('.venv/stealth_scraper_ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Force headless to False
content = content.replace(
    'if headless:',
    'headless = False\n    if headless:'
)

# 2. Add human scroll behavior to process_product_page
import_time = "import time\nimport random"
if "import random" not in content:
    content = content.replace("import time", import_time)

human_scroll_js = """        # Human-like scrolling before finding price
        try:
            log_message("👀 Імітую читання сторінки людиною (плавний скролінг)...")
            driver.execute_script("window.scrollTo({top: Math.random() * 500 + 300, behavior: 'smooth'});")
            time.sleep(random.uniform(1.5, 3.2))
            driver.execute_script("window.scrollTo({top: Math.random() * 800 + 800, behavior: 'smooth'});")
            time.sleep(random.uniform(1.0, 2.5))
            driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            time.sleep(random.uniform(1.0, 2.0))
        except: pass
"""

content = content.replace(
    'handle_captcha(driver, "Магазинний браузер")',
    'handle_captcha(driver, "Магазинний браузер")\n' + human_scroll_js
)

# 3. Add random delays between rows
content = content.replace(
    'time.sleep(random.uniform(2, 4))',
    'time.sleep(random.uniform(3.5, 7.8)) # Human delay'
)

# 4. Remove driver_search since we only use OpenAI for search now.
# Wait, foreign_price_scraper_ai.py initializes two browsers!
# Let's just leave it alone, it doesn't hurt. We only use driver_store for API links.

with open('.venv/stealth_scraper_ai.py', 'w', encoding='utf-8') as f:
    f.write(content)

