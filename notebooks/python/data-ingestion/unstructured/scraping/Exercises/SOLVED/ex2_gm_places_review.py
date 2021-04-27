from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

N_MAX = 20
MAX_WAIT = 10
MAX_SCROLLS = 50


# function to interact with Google Maps page using Selenium
def expand_review(driver):
    # use XPath to load complete reviews
    links = driver.find_elements_by_xpath('//a[@class=\'section-expand-review blue-link\']')
    for l in links:
        l.click()


options = Options()
# options.add_argument("--headless")
options.add_argument("--window-size=1366,768")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(chrome_options=options)

# create collection
client = MongoClient('mongodb://localhost:27017/')
db = client['bip']['gm_review']

# set unique identifier based on scraped data
db.create_index('id_review', unique=True)

urls = open('places_gm.txt')
for url in urls:

    # get first page of reviews and process
    driver.get(url)

    wait = WebDriverWait(driver, MAX_WAIT)

    # go to review page
    link_review = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.widget-pane-link'))).click()

    # wait to reviews container to load
    reviews_container = 'div.section-listbox.section-scrollbox.scrollable-y.scrollable-show'
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, reviews_container)))

    # load reviews and count to reach the requested number
    n_reviews_loaded = len(driver.find_elements_by_css_selector('div.section-review-content'))
    n_scrolls = 0
    while n_reviews_loaded < N_MAX and n_scrolls < MAX_SCROLLS:

        # get div container of reviews
        scrollable_div = driver.find_element_by_css_selector(reviews_container)

        # scroll div to trigger reviews loading
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)

        # wait for reviews to load
        time.sleep(3)

        # expand reviews
        expand_review(driver)

        # count reviews to check if enough
        n_reviews_loaded = len(driver.find_elements_by_css_selector('div.section-review-content'))
        print n_reviews_loaded

        n_scrolls += 1

    # parse loaded reviews with BeautifulSoup
    response = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = response.find_all('div', class_='section-review-content')
    count = 0
    for idx, review in enumerate(reviews):

        # get review id
        id_review = review.find('button', class_='section-review-action-menu')['data-review-id']

        # get review date
        # NOTE: date is a string, it needs other processing to become a Date object
        review_date = review.find('span', class_='section-review-publish-date').text.encode('utf-8')

        # get reviewer information
        # username
        username = review.find('div', class_='section-review-title').find('span').text.encode('utf-8')

        # number of reviewer photos
        n_reviews_photos = review.find('div', class_='section-review-subtitle').find_all('span')[1].text.encode('utf-8')
        metadata = n_reviews_photos.split('\xe3\x83\xbb')
        if len(metadata) == 3:
            n_photos = int(metadata[2].split(' ')[0].replace('.', ''))
        else:
            n_photos = 0

        # number of reviews
        idx = len(metadata)
        n_reviews = int(metadata[idx-1].split(' ')[0].replace('.', ''))

        # get rating of review
        rating_raw = review.find('span', class_='section-review-stars')['aria-label']
        rating_review = int(rating_raw.split(' ')[1])

        # get review complete text
        try:
            caption = review.find('span', class_='section-review-text').text
        except Exception as e:
            # print e
            caption = None

        # build review item
        item = {

            'id_review': id_review,
            'caption': caption,
            'date': review_date,
            'rating': rating_review,
            'username': username,
            'n_review_user': n_reviews,
            'n_photo_user': n_photos,
            'timestamp': datetime.today()
        }

        try:
            db.insert_one(item)
            count += 1
        except DuplicateKeyError as e:
            print (e)

    print ('Inserted {} new reviews'.format(count))

# close resources
urls.close()
driver.close()
driver.quit()
client.close()
