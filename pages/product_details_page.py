from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class ProductDetailsPage(BasePage):
    def __init__(self, page: Page):
        self.page = page

        self.product_title: Locator = self.page.locator('.product-information h2')
        self.product_quantity: Locator = self.page.locator('#quantity')
        self.add_to_cart_btn: Locator = self.page.get_by_role('button', name='Add to cart')
        self.view_cart_btn: Locator = self.page.get_by_role('link', name='View Cart')