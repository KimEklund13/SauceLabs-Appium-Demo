"""
tests/test_add_to_cart.py
──────────────────────────
TC-02 — Browse products, add an item, verify the cart reflects the correct
        product and a quantity of 1.
"""

import pytest
from config.caps               import VALID_USERNAME, VALID_PASSWORD
from pages.login_page          import LoginPage
from pages.products_page       import ProductsPage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page           import CartPage


class TestAddToCart:

    @pytest.fixture(autouse=True)
    def pages(self, request):
        platform = request.config.getoption("--platform")
        driver = request.getfixturevalue(
            "android_driver" if platform == "android" else "ios_driver"
        )
        self.login_page    = LoginPage(driver)
        self.products_page = ProductsPage(driver)
        self.detail_page   = ProductDetailPage(driver)
        self.cart_page     = CartPage(driver)

    @pytest.mark.android
    def test_add_to_cart_android(self, android_driver):
        self.login_page.navigate_to_login().login(VALID_USERNAME, VALID_PASSWORD)
        self.products_page.wait_for_products_screen()

        self.products_page.tap_first_product()
        product_title = self.detail_page.get_product_title()

        self.detail_page.tap_add_to_cart()
        self.detail_page.assert_cart_badge_count(1)

        self.products_page.tap_cart_icon()
        self.cart_page.assert_product_in_cart(product_title)

    @pytest.mark.ios
    def test_add_to_cart_ios(self, ios_driver):
        self.login_page.navigate_to_login().login(VALID_USERNAME, VALID_PASSWORD)
        self.products_page.wait_for_products_screen()

        self.products_page.tap_first_product()
        product_title = self.detail_page.get_product_title()

        self.detail_page.tap_add_to_cart()
        self.detail_page.assert_cart_badge_count(1)

        self.products_page.tap_cart_icon()
        self.cart_page.assert_product_in_cart(product_title)