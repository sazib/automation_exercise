import logging
import time

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from pages.products_page import ProductsPage


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.log = logging.getLogger(__name__)

        self.home_link: Locator = self.page.get_by_role('link', name='Home')
        self.all_products_title: Locator = self.page.locator('h2.title.text-center')
        self.products_button: Locator = self.page.get_by_role('link', name='Products')
        self.product_name: Locator = self.page.locator('.productinfo p')

        self.homepage_title_text: str = 'Automation Exercise'

    def click_products_button(self):
        """Click on Products button"""
        self.click_and_wait(self.products_button, 10)
        return ProductsPage(self.page)

    def view_product_by_name(self, product_name):
        view_product_locator = f'//*[text()="{product_name}"]/ancestor::*/*[@class="productinfo text-center"]/../following-sibling::*//a[text()="View Product"]'
        self.page.click(view_product_locator)

    def get_product_name(self,  product_number=0):
        try:
            return self.product_name.all()[product_number].inner_text()
        except IndexError as e:
            self.log.error(f'No item found with index {product_number}')

    def view_product_by_position(self, product_number=0):
        self.log.info(f'Clicking on View Product button for item {product_number}...')
        self.page.locator('//a[text()="View Product"]').nth(product_number).click(timeout=60000)
        self.log.info(f'View details page opened successfully for product {product_number}...')

