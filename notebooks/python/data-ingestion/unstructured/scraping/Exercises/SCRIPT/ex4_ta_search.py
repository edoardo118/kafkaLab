from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

MAX_WAIT = 10


# ex1 code as a function
def get_place_data(response):
    # prepare a dictionary to store results
    place = {}

    # get place name
    name = response.find('h1', attrs={'id': 'HEADING'}).text
    place['name'] = name

    # get number of reviews
    num_reviews = response.find('span', class_='reviewCount').text
    num_reviews = int(num_reviews.split(' ')[0].replace('.', ''))
    place['review'] = num_reviews

    # get rating using a regular expression to find the correct class
    overall_rating = response.find('span', {"class": re.compile("ui_bubble_rating\sbubble_..")})['alt']
    overall_rating = float(overall_rating.split(' ')[1].replace(',', '.'))
    place['rating'] = overall_rating

    # get address
    complete_address = response.find('span', class_='detail').text
    place['address'] = complete_address

    # get ranking
    ranking_string = response.find('span', class_='header_popularity popIndexValidation ').text
    absolute_rank = int(ranking_string.split(' ')[1])
    ranking_length = float(ranking_string.split(' ')[3].replace('.', ''))
    place['ranking_str'] = ranking_string
    place['ranking_abs'] = absolute_rank
    place['ranking_rel'] = float(absolute_rank) / ranking_length

    # get tags
    tags = response.find('div', class_='detail').text.split(',')
    place['tags'] = [t.strip() for t in tags]

    return place


options = Options()
options.add_argument("--window-size=1366,768")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(chrome_options=options)

# create collection using scraped id as unique identifier
client = MongoClient('mongodb://localhost:27017/')
db = client['bip']['ta_place']
db.drop()
db.create_index('id_location', unique=True)

# get main page and refresh because of pop-up
webpage = 'https://www.tripadvisor.it'
driver.get(webpage)
driver.refresh()

# open the search bar
driver.find_element_by_css_selector('div.brand-global-nav-action-search-Search__searchButton--2dmUT').click()

# define a string query and start the search
query = 'milano'
search_bar = driver.find_element_by_id('mainSearch')
search_bar.send_keys(query)
search_bar.send_keys(Keys.RETURN)

# specify the sublist (restaurants, hotels, places,...
subfilter = 'Cose da fare'  # Ristoranti, Hotel
wait = WebDriverWait(driver, MAX_WAIT)

field_bt = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, subfilter)))
field_bt.click()

# wait for search results to load
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.search-results-list')))

response = BeautifulSoup(driver.page_source, 'html.parser')

# parse results and store url
results_list = response.find_all('div', class_='result-title')
for elem in results_list:
    features = elem['onclick'].split(',')

    url = webpage + features[3].lstrip()[1:-1]
    elem_type = features[4].split(': ')[1][1:-1]
    locationId = int(features[7].split(': ')[1][1:-1])

    print (locationId, elem_type, url)

    # insert the page
    try:
        db.insert_one({'id_location': locationId, 'type': elem_type, 'url': url})
    except DuplicateKeyError as e:
        print (e)

    # get page
    driver.get(url)
    resp = BeautifulSoup(driver.page_source, 'html.parser')

    # scrape place data
    place_data = get_place_data(resp)

    # update the DB
    try:
        db.update_one({'id_location': locationId}, {'$set': place_data}, upsert=False)
    except Exception as e:
        print (e)

# close driver and quit
driver.close()
driver.quit()
client.close()
