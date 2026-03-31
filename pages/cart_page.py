"""
pages/cart_page.py
──────────────────
Page Object for the Cart / Basket screen.
"""

from selenium.common.exceptions import TimeoutException
from pages.base_page             import BasePage
from pages.locators              import CartLocators


class CartPage(BasePage):

    @property
    def _cart_screen(self):
        return self.resolve_locator(CartLocators.CART_SCREEN_ANDROID, CartLocators.CART_SCREEN_IOS)

    @property
    def _cart_items(self):
        return self.resolve_locator(CartLocators.CART_ITEMS_ANDROID, CartLocators.CART_ITEMS_IOS)

    @property
    def _item_name(self):
        return self.resolve_locator(CartLocators.ITEM_NAME_ANDROID, CartLocators.ITEM_NAME_IOS)

    @property
    def _item_qty(self):
        return self.resolve_locator(CartLocators.ITEM_QTY_ANDROID, CartLocators.ITEM_QTY_IOS)

    # ── State queries ──────────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self.is_element_present(self._cart_screen)

    def get_item_count(self) -> int:
        try:
            self.wait_for_element(self._cart_items, timeout=10)
        except TimeoutException:
            return 0
        by, value = self._cart_items
        return len(self.driver.find_elements(by, value))

    def get_first_item_name(self) -> str:
        return self.get_text(self._item_name)

    def get_first_item_quantity(self) -> int:
        return int(self.get_text(self._item_qty))

    # ── Assertions ─────────────────────────────────────────────────────────────

    def assert_product_in_cart(self, expected_name: str, expected_qty: int = 1) -> None:
        assert self.is_loaded(), "Cart screen did not load after tapping the cart icon."
        actual_count = self.get_item_count()
        assert actual_count == 1, (
            f"Expected 1 line-item in cart, found {actual_count}."
        )
        actual_name = self.get_first_item_name()
        assert actual_name == expected_name, (
            f"Cart item name mismatch. Expected '{expected_name}', got '{actual_name}'"
        )
        actual_qty = self.get_first_item_quantity()
        assert actual_qty == expected_qty, (
            f"Expected quantity {expected_qty}, got {actual_qty}."
        )