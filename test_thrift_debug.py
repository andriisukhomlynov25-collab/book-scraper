import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By

options = uc.ChromeOptions()
options.add_argument("--window-size=1920,1080")
driver = uc.Chrome(options=options, version_main=147)
url = "https://www.thriftbooks.com/w/pen-and-ink-drawing-a-series-of-drawings-showing-its-perfect-adaptability-to-the-modern-processes-of-reproduction_george-hartnell-bartlett/20661764/?srsltid=AfmBOoq7O4h6fYMDjchfOlpG-iK5Y3Q25QUNrX3xPs0KBgD-xre4KPqd#edition=68402468&idiq=59708386"
driver.get(url)
time.sleep(5)
try:
    print(driver.find_element(By.CSS_SELECTOR, "body").text[:2000])
except Exception as e:
    print(e)
driver.quit()
