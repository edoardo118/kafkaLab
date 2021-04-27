from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient

MAX_WAIT = 10

# Option object allows to set several options for the driver
options = Options()

# size of the browser window automatically opened
options.add_argument("--window-size=1366,768")

# useful to avoid pop-up during automatic navigation
options.add_argument("--disable-notifications")

# Selenium (Chrome) driver with the options defined
driver = webdriver.Chrome(chrome_options=options)

# set up DB connection for saving results
client = MongoClient('mongodb://localhost:27017/')
db = client['bip']['gm_place']

# input file, containing a list of urls
urls = open('places_gm.txt')

# iterate over the file and scrape data from each url
for url in urls:

    # get the page
    driver.get(url)

    # wait for content to load
    wait = WebDriverWait(driver, MAX_WAIT)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.section-star-display')))

    # send the page extracted with Selenium to BeautifulSoap parser
    response = BeautifulSoup(driver.page_source, 'html.parser')

    # prepare a dictionary to store results
    place = {}

    # get place name
    name = response.find('h1', class_='section-hero-header-title').text
    place['name'] = name

    # get number of reviews
    n_reviews = response.find('button', class_='widget-pane-link').text.replace('.', '')

    # casting to correct type
    n_reviews = int(n_reviews.split(' ')[0])
    place['review'] = n_reviews

    # get rating using a regular expression to find the correct class
    overall_rating = overall_rating = response.find('span', class_='section-star-display').text

    # casting to correct type
    overall_rating = float(overall_rating.replace(',', '.'))
    place['rating'] = overall_rating

    # get address
    complete_address = response.find('div', class_='section-info-line').text
    place['address'] = complete_address.strip()

    # get type of place
    type = response.find('span', class_='section-rating-term').text
    place['type'] = type

    # save result into MongoDB collection
    db.insert_one(place)

# close file
urls.close()

# close driver and quit
driver.close()
driver.quit()

# close db connection
client.close()


