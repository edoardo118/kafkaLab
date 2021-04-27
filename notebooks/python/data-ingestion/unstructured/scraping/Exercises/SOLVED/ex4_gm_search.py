from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

MAX_WAIT = 10


def get_place_data(response):
    # prepare a dictionary to store results
    place = {}

    # get place name
    name = response.find('h3', class_='section-result-title').text
    place['name'] = name.strip()

    try:
        # get number of reviews
        n_reviews = response.find('span', class_='section-result-num-ratings')['aria-label']

        # casting to correct type or set to 0 if not present
        n_reviews = int(n_reviews.split(' ')[1])
    except:
        n_reviews = 0

    place['review'] = n_reviews

    try:
        # get rating using a regular expression to find the correct class
        overall_rating = response.find('span', class_='cards-rating-score').text

        # casting to correct type
        overall_rating = float(overall_rating.replace(',', '.'))
    except:
        overall_rating = 0.0

    place['rating'] = overall_rating

    # get address
    complete_address = response.find('span', class_='section-result-location').text
    place['address'] = complete_address.strip()

    # get type of place
    type = response.find('span', class_='section-result-details').text
    place['type'] = type

    return place


options = Options()
options.add_argument("--window-size=1366,768")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(chrome_options=options)

# create collection using scraped id as unique identifier
client = MongoClient('mongodb://localhost:27017/')
db = client['bip']['gm_place']
db.drop()

# get main page and refresh because of pop-up
webpage = 'https://www.google.it/maps'
driver.get(webpage)

# define a string query and start the search
# NOTE: Google Maps check browser geolocalization
query = 'bar'
search_bar = driver.find_element_by_id('searchboxinput')
search_bar.send_keys(query)
search_bar.send_keys(Keys.RETURN)

# wait for search results to load
wait = WebDriverWait(driver, MAX_WAIT)
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.section-compact-filters')))
response = BeautifulSoup(driver.page_source, 'html.parser')

place_list = response.find_all('div', class_='section-result-content')

# scrape data from search results
for place in place_list:
    p = get_place_data(place)
    db.insert_one(p)

    print (p)

# close driver and quit
driver.close()
driver.quit()
client.close()
