import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_details_page import ProductDetailsPage
from pages.products_page import ProductsPage
from testcases.base_test import BaseTest


class TestCartFunctionalitie(BaseTest):
    @pytest.fixture(autouse=True)
    def setup_ttestsuite(self, request):
        self.home_page = HomePage(request.cls.page)
        self.products_page = ProductsPage(request.cls.page)
        self.product_details_page = ProductDetailsPage(request.cls.page)

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_add_to_cart(self):
        """
        Test case to verify product search functionality

        Steps:
        1. Launch browser
        2. Navigate to https://automationexercise.com/
        3. Verify that homepage is visible successfully
        4. Click 'View Product' for any product on home page
        5. Verify product detail is opened
        6. Increase quantity to 4
        7. Click 'Add to cart' button
        8. Click 'View Cart' button
        9. Verify that product is displayed in cart page with exact quantity
        """
        items_to_purchase = '4'

        with allure.step('Verify that homepage is visible'):
            expect(self.home_page.home_link).to_have_css('color', 'rgb(255, 165, 0)')
        product_name = self.home_page.get_product_name()
        self.home_page.view_product_by_position()
        with allure.step('Verify product details page is landed successfully'):
            assert '/product_details/' in self.page.url
            expect(self.product_details_page.product_title).to_have_text(product_name)

        self.product_details_page.product_quantity.fill(items_to_purchase)
        self.product_details_page.add_to_cart_btn.click()
        self.product_details_page.view_cart_btn.click()

        with allure.step('Verify that product is displayed in cart page with exact quantity'):
            expect(CartPage(self.page).quantity).to_have_text(items_to_purchase)
