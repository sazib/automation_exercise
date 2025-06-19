"""
Provides generic methods for interacting with application UI using playwright library at the core.
"""
import time
from logging import Logger

from playwright.sync_api import Page, Locator


class BasePage:
    """
    Contains methods for basic page interaction. All the methods are wrapper around selenium
    webdriver methods.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = Logger('test')

    def navigate(self, url):
        self.page.goto(url)

    @staticmethod
    def wait_for(max_wait=15):
        time.sleep(max_wait)

    @staticmethod
    def get_element_text(selector: Locator) -> str:
        """Get text from an element"""
        return selector.inner_text().strip()

    @classmethod
    def fill_input(cls, selector: Locator, value: str):
        """Fill an input field"""
        selector.fill(value)

    @classmethod
    def click_and_wait(cls, selector: Locator, max_wait_time=0):
        """Click an element"""
        selector.click()
        time.sleep(max_wait_time)

