from selenium import webdriver

browser = webdriver.PhantomJS()
browser.get("http://www.anthropologie.eu/anthro/index.jsp#/")
html = browser.page_source
print(html)
