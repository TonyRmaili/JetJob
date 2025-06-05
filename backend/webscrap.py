from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

'''
Not used!
'''



# Setup Chrome headless
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load the page
driver.get("https://arbetsformedlingen.se/platsbanken/")

# Wait for content to load (adjust as needed)
time.sleep(3)

# Get the full rendered HTML
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Save to file or print
with open("rendered_page.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())

driver.quit()
