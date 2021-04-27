from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient

# Option object allows to set several options for the driver
options = Options()

# headless: run browser without the graphical interface (mandatory for remote running on Virtual Machines)
# options.add_argument("--headless")

# size of the browser window automatically opened
options.add_argument("--window-size=1366,768")

# useful to avoid pop-up during automatic navigation
options.add_argument("--disable-notifications")

# Selenium (Chrome) driver with the options defined
driver = webdriver.Chrome(chrome_options=options)

# set up DB connection for saving results
client = MongoClient('mongodb://localhost:27017/')
db = client['bip']['ta_place']

# input file, containing a list of urls
urls = open('places.txt')

# iterate over the file and scrape data from each url
for url in urls:

    # get the page (equivalent to use requests)
    driver.get(url)

    # send the page extracted with Selenium to BeautifulSoap parser
    response = BeautifulSoup(driver.page_source, 'html.parser')

    # prepare a dictionary to store results
    place = {}

    # get place name
    name = response.find('h1', attrs={'id': 'HEADING'}).text
    place['name'] = name

    # get reviews
    num_reviews = response.find('span', class_='reviewCount').text

    # casting to correct type
    num_reviews = int(num_reviews.split(' ')[0].replace('.', ''))
    place['review'] = num_reviews

    # get rating using a regular expression
    overall_rating = response.find('span', {"class": re.compile("ui_bubble_rating\sbubble_..")})['alt']

    # casting to correct type
    overall_rating = float(overall_rating.split(' ')[1].replace(',', '.'))
    place['rating'] = overall_rating

    # get address
    complete_address = response.find('span', class_='detail').text
    place['address'] = complete_address

    # get ranking
    ranking_string = response.find('span', class_='header_popularity popIndexValidation ').text

    # casting to correct type
    absolute_rank = int(ranking_string.split(' ')[1])
    ranking_length = float(ranking_string.split(' ')[3].replace('.', ''))

    # keep original string field, too
    place['ranking_str'] = ranking_string
    place['ranking_abs'] = absolute_rank
    place['ranking_rel'] = float(absolute_rank)/ranking_length

    # get tags list
    tags = response.find('div', class_='detail').text.split(',')

    # strip() removes leading and trailing spaces
    place['tags'] = [t.strip() for t in tags]

    # save result into MongoDB collection
    db.insert_one(place)

# close file
urls.close()

# close driver and quit
driver.close()
driver.quit()

# close db connection
client.close()


