"""
pages/products_page.py
──────────────────────
Page Object for the Products catalog screen — the landing screen after login.
"""

from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from pages.locators  import Nav, ProductsLocators


class ProductsPage(BasePage):

    @property
    def _header(self):
        return self.resolve_locator(ProductsLocators.HEADER_ANDROID, ProductsLocators.HEADER_IOS)

    @property
    def _first_product(self):
        return self.resolve_locator(
            ProductsLocators.FIRST_PRODUCT_ANDROID,
            ProductsLocators.FIRST_PRODUCT_IOS
        )

    @property
    def _cart(self):
        return self.resolve_locator(Nav.CART_ANDROID, Nav.CART_IOS)

    # ── State queries ──────────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self.is_element_present(self._header)

    def is_logged_in(self) -> bool:
        if self.is_ios:
            self.tap((AppiumBy.ACCESSIBILITY_ID, "More-tab-item"))
            result = self.is_element_present((AppiumBy.ACCESSIBILITY_ID, "LogOut-menu-item"), timeout=5)
            self.tap((AppiumBy.ACCESSIBILITY_ID, "Catalog-tab-item"))
            return result
        return self.is_loaded()

    # ── Actions ────────────────────────────────────────────────────────────────

    def wait_for_products_screen(self) -> "ProductsPage":
        """
        Block until the Products header is visible.
        Call this after login — the screen loads asynchronously and we need
        to wait before any catalog interaction.
        """
        self.wait_for_element(self._header)
        return self

    def tap_first_product(self) -> "ProductsPage":
        self.wait_for_element(self._first_product)
        by, value = self._first_product
        self.driver.find_elements(by, value)[0].click()
        return self

    def tap_cart_icon(self) -> "ProductsPage":
        self.tap(self._cart)
        return self