"""
pages/product_detail_page.py
─────────────────────────────
Page Object for the individual Product Detail screen.
"""

from pages.base_page import BasePage
from pages.locators  import ProductDetailLocators


class ProductDetailPage(BasePage):

    @property
    def _product_title(self):
        return self.resolve_locator(
            ProductDetailLocators.PRODUCT_TITLE_ANDROID,
            ProductDetailLocators.PRODUCT_TITLE_IOS
        )

    @property
    def _add_to_cart_btn(self):
        return self.resolve_locator(
            ProductDetailLocators.ADD_TO_CART_ANDROID,
            ProductDetailLocators.ADD_TO_CART_IOS
        )

    @property
    def _cart_badge(self):
        # iOS does not expose the cart badge count as an accessible element.
        # resolve_locator handles None — get_cart_badge_count checks for None
        # before attempting a find, and assert_cart_badge_count skips on iOS.
        return self.resolve_locator(
            ProductDetailLocators.CART_BADGE_ANDROID,
            ProductDetailLocators.CART_BADGE_IOS
        )

    # ── State queries ──────────────────────────────────────────────────────────

    def get_product_title(self) -> str:
        return self.get_text(self._product_title)

    def get_cart_badge_count(self) -> int:
        if self._cart_badge is None:
            return -1  # iOS — badge not accessible, caller should skip assertion
        if not self.is_element_present(self._cart_badge, timeout=5):
            return 0
        return int(self.get_text(self._cart_badge))

    # ── Actions ────────────────────────────────────────────────────────────────

    def tap_add_to_cart(self) -> "ProductDetailPage":
        self.tap(self._add_to_cart_btn)
        return self

    # ── Assertions ─────────────────────────────────────────────────────────────

    def assert_cart_badge_count(self, expected: int) -> None:
        actual = self.get_cart_badge_count()
        if actual == -1:
            return  # iOS — badge count not accessible, skip silently
        assert actual == expected, (
            f"Cart badge expected {expected} after adding one item, got {actual}. "
            f"Add to Cart may not have registered."
        )