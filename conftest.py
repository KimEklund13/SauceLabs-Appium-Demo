"""
conftest.py
───────────
pytest looks for this file automatically. Anything defined here is available
to every test file in the project without needing an import.

The most important thing this file does: manage the Appium driver lifecycle.

WHY fixtures instead of setUp/tearDown (the unittest style)?
  pytest fixtures are more composable. A test can declare exactly which
  fixtures it needs — and only those run. With setUp/tearDown, every method
  in the class shares the same setup even if some tests don't need it.
  Fixtures also have explicit scope control (function, class, session) so
  you can choose whether to spin up one driver per test or one per session.

WHY function scope (one driver per test)?
  Each test gets a fresh app session. This costs time (~5-10 seconds per
  test for app launch) but means tests are completely isolated — a crash or
  bad state in test A can't affect test B.

  In a more mature pipeline you'd experiment with class or session scope +
  a reset mechanism (e.g., app.reset() or clearing app state via API) to
  trade some isolation for speed.
"""

import pytest
import logging
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy

from config.caps import ANDROID_CAPS, IOS_CAPS, APPIUM_URL

logger = logging.getLogger(__name__)


# ── CLI option ─────────────────────────────────────────────────────────────────
def pytest_addoption(parser):
    """
    Adds a --platform flag to the pytest command line.
    Usage:
      pytest --platform=android
      pytest --platform=ios
      pytest --platform=both

    WHY a CLI flag rather than separate test files or markers?
      One command, one flag — the person running the suite doesn't need to
      know which files to include/exclude. It also makes CI pipelines clean:
      the Android job passes --platform=android, the iOS job passes --platform=ios.
    """
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        choices=["android", "ios", "both"],
        help="Which platform to run tests on: android | ios | both",
    )


# ── Driver factory ─────────────────────────────────────────────────────────────
def _create_driver(caps: dict):
    """
    Spins up an Appium WebDriver session from a capabilities dict.

    AppiumOptions is the modern way to pass capabilities in Appium 2.
    The older dict-only approach was deprecated because it mixed
    standard W3C capabilities with Appium-specific ones unsafely.

    WHY implicitly_wait(0)?
      Mixing implicit and explicit waits causes unpredictable double-wait
      behaviour — if you set implicit_wait to 10s AND your explicit wait
      is 10s, a missing element can take 20s to fail. We set implicit
      to 0 and handle ALL waiting explicitly in the page objects.
      This makes timeouts predictable and debuggable.
    """
    options = AppiumOptions()
    options.load_capabilities(caps)

    logger.info("Starting Appium session → platform: %s", caps.get("platformName"))
    driver = webdriver.Remote(APPIUM_URL, options=options)
    driver.implicitly_wait(0)   # Explicit waits only — see WHY above
    return driver


# ── Android fixture ────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def android_driver(request):
    """
    Yields a live Appium driver connected to an Android device/emulator.
    After the test completes (pass or fail), driver.quit() ends the session
    and releases the device.

    WHY pytest.skip instead of an if-block that just doesn't yield?
      pytest.skip marks the test as SKIPPED (not failed, not passed) which
      is the correct signal when a test was intentionally not executed.
      A CI dashboard can show "X tests skipped" rather than confusing absence.
    """
    if request.config.getoption("--platform") == "ios":
        pytest.skip("Skipping Android — --platform=ios was specified")

    driver = _create_driver(ANDROID_CAPS)
    yield driver        # The test runs here
    driver.quit()       # Always runs — even if the test fails
    logger.info("Android Appium session closed")


# ── iOS fixture ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def ios_driver(request):
    if request.config.getoption("--platform") == "android":
        pytest.skip("Skipping iOS — --platform=android was specified")

    driver = _create_driver(IOS_CAPS)
    yield driver
    driver.quit()
    logger.info("iOS Appium session closed")


# ── Parameterizing the tests based on driver  ────────────────────────────────────────
@pytest.fixture
def driver(request):
    platform = request.config.getoption("--platform")
    caps = ANDROID_CAPS if platform == "android" else IOS_CAPS
    drv = _create_driver(caps)
    yield drv
    drv.quit()
    logger.info(f"{platform.upper()} Appium session closed")