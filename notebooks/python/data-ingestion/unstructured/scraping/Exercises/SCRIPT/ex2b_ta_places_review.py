from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

N_MAX = 20
MAX_WAIT = 10


# function to interact with Tripadvisor page using Selenium
def expand_review(driver):

    # programmatically wait
    wait = WebDriverWait(driver, MAX_WAIT)

    # load the complete review text in the HTML
    try:
        # wait until the element is clickable
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.taLnk.ulBlueLinks'))).click()

        # wait complete reviews to load
        time.sleep(5)

    # It is raised only if there is no link for expansion (e.g.: set of short reviews)
    except Exception as e:
        print (e)


# function to parse a page of reviews
def get_review_data(resp, db):

    # save place name along with review
    name = resp.find('h1', attrs={'id': 'HEADING'}).text
    r_list = resp.find_all('div', class_='review-container')

    reviews = 0
    for idx, review in enumerate(r_list):

        # get review id
        id_review = int(review['data-reviewid'])

        # get review date
        # NOTE: date is a string, it needs other processing to become a Date object
        review_date = review.find('span', class_='ratingDate')['title']

        # get reviewer information: username, number of reviews, location
        info_text = review.find('div', class_='info_text')
        username = info_text.find('div', class_=None).text.encode('utf-8')

        # location is not present for each user
        if info_text.find('div', class_='userLoc') is not None:
            location = info_text.find('div', class_='userLoc').text.encode('utf-8')
        else:
            location = None

        # number of reviews is not present for each user
        if review.find('span', class_='badgetext') is not None:
            n_user_reviews = int(review.find('span', class_='badgetext').text)
        else:
            n_user_reviews = None

        # get rating of review using regular expression
        rating_raw = review.find('span', {"class": re.compile("ui_bubble_rating\sbubble_..")})['class'][1][-2:]
        rating_review = float(rating_raw[0] + '.' + rating_raw[1])

        # get review title
        title = review.find('span', class_='noQuotes').text

        # get review complete text
        caption = review.find('p', class_='partial_entry').text

        # build review item
        item = {

            'name': name,
            'id_review': id_review,
            'title': title,
            'caption': caption,
            'date': review_date,
            'rating': rating_review,
            'username': username,
            'n_review_user': n_user_reviews,
            'location': location
        }

        try:
            db.insert_one(item)
            reviews += 1
        except DuplicateKeyError as e:
            print (e)

    return reviews


options = Options()
# options.add_argument("--headless")
options.add_argument("--window-size=1366,768")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(chrome_options=options)

# create collection using scraped id as unique identifier
client = MongoClient('mongodb://localhost:27017/')
db = client['bip']['ta_review']

# set unique identifier based on scraped data
db.create_index('id_review', unique=True)


urls = open('places.txt')
for url in urls:

    # get first page of reviews and process
    driver.get(url)

    # scroll and move to the filter section
    driver.execute_script('window.scrollBy(0,2000)')

    # scroll and click
    expand_review(driver)

    # send the page manipulated with Selenium to BeautifulSoup parser
    response = BeautifulSoup(driver.page_source, 'html.parser')

    # return the number of scraped reviews
    n_reviews = get_review_data(response, db)

    page_number = 1
    while n_reviews < N_MAX:
        page_number += 1

        driver.execute_script('window.scrollBy(0,1000)')
        driver.find_element_by_link_text(str(page_number)).click()
        time.sleep(3)

        expand_review(driver)
        response = BeautifulSoup(driver.page_source, 'html.parser')
        n_reviews += get_review_data(response, db)

# close resources
urls.close()
driver.close()
driver.quit()
client.close()
