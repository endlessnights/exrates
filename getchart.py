import urllib
from selenium import webdriver

driver = webdriver.Chrome
element = driver.find_element("id", "myChart")
src = element.get_attribute('src')
urllib.retrieve(src, "chart.png")
driver.close()