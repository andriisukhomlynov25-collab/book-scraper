import os
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By

_DRIVER_PATH = os.path.expanduser(
    "~/Library/Application Support/undetected_chromedriver/undetected_chromedriver"
)

options = uc.ChromeOptions()
options.add_argument("--window-size=1920,1080")
driver = uc.Chrome(options=options, version_main=147, driver_executable_path=_DRIVER_PATH)
driver.get("https://www.booksamillion.com/p/Pen-Ink-Drawing/George-Hartnell-Bartlett/9781016901239")
time.sleep(5)
try:
    print(driver.find_element(By.TAG_NAME, "body").text[:2000])
except Exception as e:
    print(e)
driver.quit()