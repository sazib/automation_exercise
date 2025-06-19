import allure
import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.products_page import ProductsPage
from testcases.base_test import BaseTest


class TestSearchFunctionalities(BaseTest):

    @pytest.fixture(scope='function', autouse='true')
    def setup_ttestsuite(self, request):
        self.home_page = HomePage(request.cls.page)
        self.products_page = ProductsPage(request.cls.page)

    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.parametrize("product_name", ["Tops"])
    def test_product_search(self, product_name):
        """
        Test case to verify product search functionality

        Steps:
        1. Launch browser
        2. Navigate to https://automationexercise.com/
        3. Verify that homepage is visible successfully
        4. Click on 'Products' button
        5. Verify user is navigated to ALL PRODUCTS page successfully
        6. Enter product name in search input and click search button
        7. Verify 'SEARCH PRODUCTS' is visible
        8. Verify all the products related to search are visible
        """
        self.page.goto(pytest.url)
        with allure.step('Verify that homepage is visible'):
            expect(self.home_page.home_link).to_have_css('color', 'rgb(255, 165, 0)')
        products_page = self.home_page.click_products_button()
        with allure.step('Verify user is navigated to ALL PRODUCTS page successfully'):
            expect(self.home_page.all_products_title).to_contain_text('All Products')
        products_page.search_product(product_name)
        with allure.step('Verify search product functionality works'):
            with allure.step('Verify user is navigated to ALL PRODUCTS page successfully'):
                expect(self.products_page.search_title).to_be_visible()
            with allure.step('Verify all the products related to search are visible'):
                  product_elements = self.home_page.product_name.all()
                  assert len(product_elements) > 0, "No products found in search results"

                  print([product.inner_text() for product in product_elements], '&'*30)
                  assert any([product_name.lower() in product.inner_text().lower() for product in product_elements])

