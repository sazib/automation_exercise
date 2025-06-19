from playwright.sync_api import Locator, Page

from pages.base_page import BasePage

class ProductsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.search_input: Locator = self.page.locator('#search_product')
        self.search_button: Locator = self.page.locator('#submit_search')
        self.search_title: Locator = self.page.locator('//h2[contains(text(), "Searched Products")]')
        self.product_cards = self.page.locator(".productinfo")

    def search_product(self, product_name: str):
        """Search for a product"""
        self.fill_input(self.search_input, product_name)
        self.click_and_wait(self.search_button)
