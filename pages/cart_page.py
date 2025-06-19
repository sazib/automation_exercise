from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class CartPage(BasePage):
      def __init__(self, page: Page):
        super().__init__(page)

        self.quantity: Locator = self.page.locator('.cart_quantity button')