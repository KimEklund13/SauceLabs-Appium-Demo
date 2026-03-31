"""
tests/test_login.py
────────────────────
Login test suite covering successful auth, invalid credentials, and
missing field validation across Android and iOS.
"""
import pytest
from config.caps      import VALID_USERNAME, VALID_PASSWORD
from pages.login_page import LoginPage


class TestLogin:

    def test_login(self, driver):
        # User should be able to successfully sign in with valid credentials
        # and see the Log Out option in the nav menu confirming auth succeeded.
        login_page = LoginPage(driver)
        login_page.navigate_to_login()
        login_page.login(VALID_USERNAME, VALID_PASSWORD)
        assert login_page.user_is_successfully_signed_in()

    @pytest.mark.xfail(
        strict=False,
        reason=(
            "Known app bug: the app accepts any password for registered usernames "
            "and silently logs the user in instead of showing a validation error. "
            "This test is intentionally left in the suite to document the bug."
        )
    )
    def test_invalid_credentials(self, driver):
        # User submitting a valid username with an incorrect password should
        # see a validation error. Known bug — expected to fail until fixed.
        login_page = LoginPage(driver)
        login_page.navigate_to_login()
        login_page.login("bob@example.com", "definitelywrong")
        assert login_page.is_error_displayed()

    def test_username_required(self, driver):
        # User submitting the form with no username but a password should
        # see a "Username is required" error.
        login_page = LoginPage(driver)
        login_page.navigate_to_login()
        login_page.login("", "somepassword")
        assert login_page.is_username_error_displayed()

    def test_password_required(self, driver):
        # User submitting the form with a username but no password should
        # see a "Password is required" error.
        login_page = LoginPage(driver)
        login_page.navigate_to_login()
        login_page.login("bob@example.com", "")
        assert login_page.is_password_error_displayed()