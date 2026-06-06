import os
import time
import undetected_chromedriver as uc

try:
    print("Initializing undetected_chromedriver...")
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1600,1000")
    # Try initializing uc
    driver = uc.Chrome(options=options)
    print("Success! Navigating to Violity...")
    driver.get("https://violity.com/ua")
    time.sleep(5)
    print(f"Violity Title: {driver.title}")
    driver.quit()
except Exception as e:
    print(f"Failed to run uc: {e}")
