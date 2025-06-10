# Failed experiment
'''from selenium import webdriver
from selenium.webdriver.common.by import By

# debug
print("e-mail: ")
x = input()
print("password: ")
y = input()

driver = webdriver.Chrome() # define driver
driver.get("https://elabftw.fisica.unina.it/login.php") # fetch url of the form
title = driver.title # get browser informations
driver.implicitly_wait(0.5) # advanced topic

email = driver.find_element(by=By.ID, value="email")
password = driver.find_element(by=By.ID, value="password")
submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

email.send_keys(x)
password.send_keys(y)
submit_button.click()

driver.quit()'''