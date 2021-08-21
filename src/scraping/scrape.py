"""
scrape.py

Scrapes historical data from Google Arts
and Culture.
"""

import random
import logging
import multiprocessing as mp

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement

from scraper import Scraper
from models import Event, Item

# scraping options
options = dict(headless=False,
               wait_time=5,
               save_file="./saved_data.json",
               auto_close=True)

# general options
NUM_EVENTS = 250
logger = logging.getLogger(__name__)


def generate_id():
    return random.randrange(10000, 99999)


def get_image_data(s: Scraper, image: WebElement) -> Item:
    """
    Get data for image.
    """

    # child scraper
    s.driver.get(image.get_attribute('href'))
    try:
        description = s('.WDSAyb.QwmCXd>div>p').get_attribute('innerText')
    except WebDriverException as w:
        print(w)
        description = ""
    metadata = s('.XD0Pkb', multiple=True)
    item = {'id': generate_id(),
            'url': image.get_attribute('href'),
            'description': description,
            'image_url': image.get_attribute('data-vbgsrc'),
            'metadata': [attr.get_attribute('innerText') for attr in metadata]}

    return Item(**item)


def get_event_data(s: Scraper, card_url) -> Event:
    """
    Gets all data for a single `event`.
    """

    d = s.driver

    # navigate to link
    event = {
        'id': generate_id(),
        'url': card_url
    }

    d.get(event['url'])

    # get event data
    event['title'] = s('.P9TrZe').get_attribute('innerText')
    event['description'] = s('.zzySAd.gI3F8b').get_attribute('innerText')
    event['date'] = s('.CazOhd').get_attribute('innerText')

    # get data for all items (images)
    s.scroll_to_bottom()
    item_urls = s('.ZEnmnd.PJLMUc', multiple=True)
    event['items'] = []

    with s.fork() as cs:
        for i, image in enumerate(item_urls):
            logger.info(i)
            try:
                item = get_image_data(cs, image)
            except Exception as e:
                print(e)
                continue
            event['items'].append(item.__dict__)

    return Event(**event)


def scrape_event(index, event):
    s = Scraper(**options)
    with s as cs:
        print(f"Started event #{index}")
        try:
            event_data = get_event_data(cs, event)
        except Exception as e:
            print(e)
            return {}
        return event_data.__dict__


def main(s: Scraper):
    """
    Entry point for scraping.
    """

    # load root page
    url = 'https://artsandculture.google.com/category/event'
    s.driver.get(url)

    # scroll until obtained minimum events
    events = []
    while len(events) < NUM_EVENTS:
        cards = s('a[href$="event"].PJLMUc', multiple=True)
        events = [card.get_attribute('href') for card in cards][:NUM_EVENTS]
        print(f"Gathering events: {len(events)}/{NUM_EVENTS}")
        s.scroll_to_bottom()

    print("Beginning scraping")
    # get data
    s.data['events'] = []
    pool = mp.Pool(1)
    s.data['events'] = pool.starmap(scrape_event, enumerate(events))


if __name__ == '__main__':
    random.seed(0)
    scraper = Scraper(**options)
    with scraper as scraper:
        main(scraper)
