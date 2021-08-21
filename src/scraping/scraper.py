"""
scraper.py

Thin around Selenium with additional features.
Supports 'forking' scrapers for parallel or
hierarchical scraping.

"""
from typing import Union, List

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
import logging
import pickle

import os

class Scraper:
    """
    Thin wrapper around Selenium. Extends core functionality.
    """

    def __init__(self, headless=False,
                 wait_time=0,
                 save_file=None,
                 root_path=None,
                 auto_close=True,
                 browser='chrome'):

        self.logger = logging.Logger('scraper', level=logging.DEBUG)

        self.config = {
            'headless': headless,
            'wait_time': wait_time,
            'save_file': save_file,
            'root_path': root_path,
            'auto_close': auto_close,
            'browser': browser
        }

        self.auto_close = auto_close
        self.root_path = root_path
        self.wait_time = wait_time
        self.save_file = save_file
        self.browser = browser

        self.headless = headless
        self.options = Options()
        self.data = {}

        if headless:
            self.options.add_argument('--headless')

    def __enter__(self):
        """
        Context Manager function. Starts driver.
        """
        if self.browser.lower() == 'chrome':
            self.driver = webdriver.Chrome(options=self.options)
        if self.browser.lower() == 'firefox':
            options = webdriver.FirefoxOptions()
            options.headless = self.headless
            self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.implicitly_wait(self.wait_time)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes drivers. If exception, save data.
        """

        if self.data:
            self.logger.info("Saving data.")
            print("SAVING DATA")  # todo remove later
            with open('saved_data.pkl', 'wb+') as f:
                pickle.dump(self.data, f)

        self.data['error'] = exc_val
        if self.auto_close:
            try:
                self.driver.close()
            except WebDriverException:
                pass

    def __call__(self, selector, multiple=False) -> Union[WebElement, List[WebElement]]:
        if multiple:
            return self.driver.find_elements_by_css_selector(selector)
        return self.driver.find_element_by_css_selector(selector)

    def save_page_as(self, title: str, path=""):
        if not path:
            if not self.root_path:
                raise Exception
            path = self.root_path
        with open(os.path.join(path, title), 'w+') as f:
            f.write(self.driver.page_source)

    def fork(self):
        """
        Create scraper with parent configuration.
        """
        return Scraper(**self.config)

    def save(self):
        pass

    def scroll_to_bottom(self):
        js_script = 'window.scrollTo(0,document.body.scrollHeight)'
        self.driver.execute_script(js_script)

    def get_driver(self) -> WebDriver:
        return self.driver
