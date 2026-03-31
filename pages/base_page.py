"""
pages/base_page.py
──────────────────
BasePage is the foundation every page object inherits from.
Its job: wrap the raw Appium driver calls in readable, reusable methods
so that page objects (and by extension, tests) never speak directly to
the driver.

WHY a base class at all?
  Without it, every page object re-implements waiting logic, platform
  detection, and element interaction. When those things need to change
  (different timeout strategy, add logging, handle a new Appium version's
  API change) you'd update every page object individually.
  With a base class, you update ONE place.

HOW this maps to the XCUITest project you shared:
  BasePage here is analogous to XCUIApplication+Extensions.swift and
  XCUIElement+Extensions.swift combined — those extension files added
  tapElement(), waitForElementToBecomeAvailable(), etc. to Apple's built-in
  types. BasePage adds the same kind of wrapping but as inherited methods
  since Python doesn't have extension methods.

  In an even more mature Python project, you might split this further:
    BaseElement  — wraps a single WebElement (tap, type, get_text)
    BasePage     — wraps the page/driver (navigate, wait for page load)
  ...similar to how iOS's XCUIElement extensions and XCUIApplication extensions
  were in separate files.
"""

import logging
from selenium.webdriver.support.ui    import WebDriverWait
from selenium.webdriver.support       import expected_conditions as EC
from selenium.common.exceptions       import TimeoutException
from appium.webdriver.common.appiumby import AppiumBy
from pages.locators import Nav

logger = logging.getLogger(__name__)

# Single source of truth for the default wait.
# If CI is slow, change this number once and every wait in every page benefits.
DEFAULT_TIMEOUT = 15


class BasePage:

    def __init__(self, driver):
        self.driver   = driver
        # Read the platform once at construction so every method can branch
        # on it without hitting the driver again.
        self._platform = driver.capabilities.get("platformName", "").lower()

    # ── Platform detection ─────────────────────────────────────────────────────

    @property
    def is_android(self) -> bool:
        return self._platform == "android"

    @property
    def is_ios(self) -> bool:
        return self._platform == "ios"

    def resolve_locator(self, android_locator: tuple, ios_locator: tuple) -> tuple:
        """
        Choose the right (By, value) tuple for the current platform.

        WHY separate locators per platform?
          Android and iOS use completely different accessibility systems.
          Android: resource-id, content-desc, XPath on android.widget.*
          iOS:     accessibilityIdentifier, XPath on XCUIElementType*

          A cross-platform app (like this React Native demo) can set the same
          testID in JS, which surfaces as content-desc on Android and
          accessibilityIdentifier on iOS — but the Appium BY strategy is
          different, so we still need two tuples.

        In a project that uses a consistent testID strategy you'd mostly
        use ACCESSIBILITY_ID on both platforms. But having the resolve_locator
        pattern available saves you when platforms diverge.
        """
        return android_locator if self.is_android else ios_locator


    # ── Waiting ────────────────────────────────────────────────────────────────

    def wait_for_element(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """
        Block until an element is VISIBLE on screen, then return it.

        WHY WebDriverWait + expected_conditions instead of find_element?
          driver.find_element() returns immediately — if the element isn't
          there yet, it throws NoSuchElementException right away.
          WebDriverWait polls the DOM every 500ms until the condition is true
          or the timeout expires. This is how you handle animation, API calls,
          and slow renders without adding sleep() calls everywhere.

        WHY visibility specifically (not just presence)?
          An element can EXIST in the DOM (present) while being invisible
          (opacity:0, off-screen, covered by another element). We almost
          always want visibility because if you can't see it, your test
          asserting against it isn't reflecting real user experience.

          Compare to iOS: this is equivalent to waitForExistence() which also
          checks that the element has rendered onto the screen.
        """
        by, value = locator
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        except TimeoutException:
            raise TimeoutException(
                f"Element not visible after {timeout}s → ({by}, '{value}')"
            )

    def wait_for_clickable(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """
        Block until an element is both visible AND enabled (clickable).

        WHY a separate method from wait_for_element?
          A button can be visible but DISABLED — grey'd out, not interactive.
          EC.element_to_be_clickable checks both. Use this before any tap.
          Use wait_for_element when you only need to READ a value.

          This maps to isHittable in XCUITest — the iOS equivalent that checks
          the element is not just present but actually interactable.
        """
        by, value = locator
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except TimeoutException:
            raise TimeoutException(
                f"Element not clickable after {timeout}s → ({by}, '{value}')"
            )

    def wait_for_element_to_vanish(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """
        Block until an element DISAPPEARS.

        WHY do we need this?
          After tapping 'Remove from cart' or dismissing a dialog, the next
          action should only fire once the previous UI element is gone.
          Without this wait, a tap can hit a disappearing element that's
          still receiving touch events during its animation.

          Maps to waitForNonExistence / waitForElementToBecomeUnhittable in the
          XCUITest extensions you showed.
        """
        by, value = locator
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((by, value))
        )

    def is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        """
        Non-throwing existence check. Returns True/False.

        WHY not just try/except around wait_for_element everywhere?
          Tests often need to make branching decisions: "if the banner is
          showing, dismiss it; otherwise continue." Having a boolean method
          makes that code readable. Callers decide what a missing element means —
          sometimes it's a test failure, sometimes it's expected.
        """
        try:
            self.wait_for_element(locator, timeout)
            return True
        except TimeoutException:
            return False

    # ── Interactions ───────────────────────────────────────────────────────────

    def tap(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """
        Wait for an element to be clickable, then tap it.

        WHY log the locator?
          When a test fails and you're reading CI output without a video,
          "Tapped: (accessibility id, 'Login button')" tells you exactly where
          execution was. This is the equivalent of the custom Logger.ui() call
          you'd add inside tapElement() in the mature XCUITest project.

          In a more mature project you'd also add a screenshot-on-failure hook
          here, or emit structured JSON for a reporting dashboard.
        """
        element = self.wait_for_clickable(locator, timeout)
        logger.info("Tapping → %s", locator)
        element.click()

    def type_text(self, locator: tuple, text: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Wait for a field, clear any existing value, then type new text.

        WHY clear() before send_keys()?
          Same reason as clearAndEnterText() in your XCUITest project — fields
          can be pre-populated by autofill, a previous test's state leak, or
          a default value. Clearing first makes the result deterministic.

          WHY not use CTRL+A / select-all?
          clear() is the cross-platform safe choice. Select-all via keys
          behaves differently on Android vs iOS and can fail on React Native
          text inputs specifically due to how RN handles native events.
        """
        element = self.wait_for_element(locator, timeout)
        element.clear()
        logger.info("Typing '%s' into → %s", text, locator)
        element.send_keys(text)

    def get_text(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> str:
        """Read the visible text of an element."""
        element = self.wait_for_element(locator, timeout)
        return element.text

    def dismiss_keyboard(self):
        if self.is_ios:
            try:
                self.driver.hide_keyboard()
                logger.info("Keyboard dismissed via hide_keyboard()")
            except Exception:
                try:
                    self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Passwords").click()
                    import time
                    time.sleep(1.5)  # wait for keyboard animation to fully complete
                    logger.info("Keyboard dismissed via Passwords button fallback")
                except Exception:
                    logger.warning("Could not dismiss keyboard")
        else:
            try:
                self.driver.hide_keyboard()
                logger.info("Keyboard dismissed via hide_keyboard()")
            except Exception:
                logger.warning("Android hide_keyboard() failed")

    def handle_system_alerts(self, action: str = "accept"):
        """
        Dismiss or accept any pending system alert (location, push notifications, etc).
        Call this after app launch before interacting with the app.
        
        WHY not autoAcceptAlerts capability?
          autoAcceptAlerts blindly accepts everything including app-level validation
          alerts we want to assert on. Handling explicitly gives us control over
          which alerts get accepted vs read and asserted on.
        """
        try:
            alert = self.driver.switch_to.alert
            logger.info(f"System alert detected: '{alert.text}' — {action}ing")
            if action == "accept":
                alert.accept()
            else:
                alert.dismiss()
        except Exception:
            pass  # no alert present, carry on

    # ── Scrolling ──────────────────────────────────────────────────────────────

    def scroll_down(self):
        """
        Swipe upward (which scrolls the content down) by ~60% of screen height.

        WHY calculate from window size rather than hardcode pixel values?
          Different device sizes (phone vs tablet, different resolutions) would
          make hardcoded coordinates scroll the wrong amount or land outside
          the screen. Percentages of the current window size work on any device.

        In a more mature project you'd also have:
          scroll_to_element(locator) — keep scrolling until the element appears
          scroll_to_text(text)       — scroll until a text label is visible
        """
        size    = self.driver.get_window_size()
        start_x = size["width"]  // 2
        start_y = int(size["height"] * 0.8)
        end_y   = int(size["height"] * 0.2)
        # duration=600ms mimics a human swipe speed — too fast can be
        # misread as a tap by some scroll views
        self.driver.swipe(start_x, start_y, start_x, end_y, duration=600)

    # ── Global Nav Methods ──────────────────────────────────────────────────────────────

    def open_nav_menu(self):
        if self.is_ios:
            self.tap(Nav.MORE_TAB_IOS)
        else:
            self.tap(Nav.HAMBURGER_ANDROID)

    def close_nav_menu(self):
        if self.is_ios:
            self.tap(Nav.CATALOG_TAB_IOS)
        else:
            self.driver.back()
