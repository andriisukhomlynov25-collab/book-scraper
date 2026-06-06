import undetected_chromedriver as uc
import time

print("Starting Chrome...")
options = uc.ChromeOptions()
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-notifications")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
try:
    driver = uc.Chrome(options=options)
    print("Chrome started successfully!")
    driver.get("https://google.com")
    time.sleep(2)
    driver.quit()
    print("Cleaned up.")
except Exception as e:
    print(f"Failed: {e}")
