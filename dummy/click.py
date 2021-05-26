from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

path = "../chromedriver.exe"
driver = webdriver.Chrome(path)

driver.get("https://techwithtim.net")
print(driver.title)


try:
    elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pg-6-1')))
    print("Page is ready!")

except TimeoutException:
    print("Timeout")

time.sleep(60)
driver.quit()
