from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from pages.locators import Nav, LoginLocators


class LoginPage(BasePage):

    # ── Platform-resolved properties ───────────────────────────────────────────

    @property
    def _username_field(self):
        return self.resolve_locator(LoginLocators.USERNAME_ANDROID, LoginLocators.USERNAME_IOS)

    @property
    def _password_field(self):
        return self.resolve_locator(LoginLocators.PASSWORD_ANDROID, LoginLocators.PASSWORD_IOS)

    @property
    def _login_button(self):
        return self.resolve_locator(LoginLocators.LOGIN_BTN_ANDROID, LoginLocators.LOGIN_BTN_IOS)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def navigate_to_login(self) -> "LoginPage":
        if self.is_android:
            self.tap(Nav.HAMBURGER_ANDROID)
            self.tap(Nav.LOGIN_MENU_ANDROID)
        else:
            self.tap(Nav.MORE_TAB_IOS)
            self.tap(Nav.LOGIN_MENU_IOS)
        return self

    # ── Actions ────────────────────────────────────────────────────────────────

    def enter_username(self, username: str) -> "LoginPage":
        self.type_text(self._username_field, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        self.type_text(self._password_field, password)
        return self

    def tap_login(self) -> "LoginPage":
        self.dismiss_keyboard()
        self.tap(self._login_button)
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        return self.enter_username(username).enter_password(password).tap_login()

    # ── State queries ──────────────────────────────────────────────────────────

    # We only keep this method for the paramterized XFAIL just for demonstration but
    # It's redundant to 'is_username_error_displayed' and 'is_password_error_displayed'
    def is_error_displayed(self) -> bool:
        return self.is_username_error_displayed() or self.is_password_error_displayed()

    def get_error_text(self) -> str:
        if self.is_ios:
            try:
                return self.driver.switch_to.alert.text
            except Exception:
                return ""
        if self.is_android:
            if self.is_element_present(LoginLocators.ERROR_MSG_ANDROID_USERNAME, timeout=2):
                return self.get_text(LoginLocators.ERROR_MSG_ANDROID_USERNAME)
            return self.get_text(LoginLocators.ERROR_MSG_ANDROID_PASSWORD)
        return self.get_text(LoginLocators.ERROR_MSG)

    def is_username_error_displayed(self) -> bool:
        if self.is_android:
            return self.is_element_present(LoginLocators.ERROR_MSG_ANDROID_USERNAME, timeout=5)
        if self.is_ios:
            try:
                alert = self.driver.switch_to.alert
                text = alert.text
                alert.accept()  # dismiss so next test starts clean
                return "username" in text.lower()
            except Exception:
                return False

    def is_password_error_displayed(self) -> bool:
        if self.is_android:
            return self.is_element_present(LoginLocators.ERROR_MSG_ANDROID_PASSWORD, timeout=5)
        if self.is_ios:
            try:
                alert = self.driver.switch_to.alert
                text = alert.text
                alert.accept()  # dismiss so next test starts clean
                return "password" in text.lower()
            except Exception:
                return False


    # ── Assertions ──────────────────────────────────────────────────────────

    def user_is_successfully_signed_in(self) -> bool:
        self.open_nav_menu()
        locator = Nav.LOGOUT_IOS if self.is_ios else Nav.LOGOUT_ANDROID
        result = self.is_element_present(locator, timeout=5)
        self.close_nav_menu()
        return result