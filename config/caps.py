"""
config/caps.py
──────────────
Appium "capabilities" are the dictionary you hand to the Appium server when
starting a session. Think of them as launch arguments that tell Appium:
  - WHAT device to use (name, OS version)
  - WHAT app to install (the .apk or .app path)
  - HOW to drive it (UiAutomator2 for Android, XCUITest for iOS)
  - EXTRA behavior flags (noReset, autoGrantPermissions, etc.)

WHY centralise capabilities here instead of writing them in every test?
  If the app package name changes, or we upgrade the iOS simulator version,
  there's one file to update rather than hunting through every test file.

WHY read from environment variables (.env file)?
  Hardcoding device names and app paths means the tests only work on YOUR
  machine. Reading from .env lets every engineer set their own local paths
  without touching committed code — and CI can inject values via secrets.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load values from the .env file in the project root.
# If .env doesn't exist, os.getenv() will just return the fallback values below.
load_dotenv()

# ── Resolve paths ──────────────────────────────────────────────────────────────
# __file__ is this caps.py file; .parent.parent climbs up to the project root.
# This lets us support both absolute paths and paths relative to the project root.
ROOT = Path(__file__).resolve().parent.parent


def _app_path(env_key: str) -> str:
    """
    Read an app path from the environment.
    If it's a relative path (e.g. apps/MyDemo.apk), resolve it
    from the project root so it works regardless of where pytest is invoked from.
    """
    raw = os.getenv(env_key, "")
    if not raw:
        return ""
    p = Path(raw)
    return str(p if p.is_absolute() else ROOT / p)


def _env(key: str, fallback: str) -> str:
    return os.getenv(key, fallback)


# ── Credentials ────────────────────────────────────────────────────────────────
# Exported so test files can import them without knowing about the env vars.
VALID_USERNAME = _env("VALID_USERNAME", "bob@example.com")
VALID_PASSWORD = _env("VALID_PASSWORD", "10203040")

# ── Appium server URL ──────────────────────────────────────────────────────────
APPIUM_HOST = _env("APPIUM_HOST", "127.0.0.1")
APPIUM_PORT = int(_env("APPIUM_PORT", "4723"))
APPIUM_URL  = f"http://{APPIUM_HOST}:{APPIUM_PORT}"


# ── Android capabilities ───────────────────────────────────────────────────────
ANDROID_CAPS = {
    # Tells Appium which mobile OS we're targeting.
    "platformName": "Android",

    # automationName: "UiAutomator2" is Google's official UI testing backend,
    # the same engine that powers Espresso under the hood.
    # Appium wraps it so we can drive it from Python instead of Kotlin/Java.
    "appium:automationName": "UiAutomator2",

    "appium:deviceName":      _env("ANDROID_DEVICE_NAME",      "emulator-5554"),
    "appium:platformVersion": _env("ANDROID_PLATFORM_VERSION", "14.0"),

    # Full path to the .apk. Appium installs it before every session.
    "appium:app":             _app_path("ANDROID_APP_PATH"),

    # appPackage + appActivity tell Appium how to LAUNCH the app after install.
    # Without these, Appium installs the app but doesn't know which activity
    # to start. Get these from `adb shell pm list packages` and the app's
    # AndroidManifest.xml, or by running `adb logcat` while launching manually.
    "appium:appPackage":      "com.saucelabs.mydemoapp.android",
    "appium:appActivity":     "com.saucelabs.mydemoapp.android.view.activities.SplashActivity",

    # noReset: False → uninstall and reinstall the app before each session.
    # This guarantees a clean state (no cached login, no leftover cart items).
    # Set to True in CI to skip reinstall and save ~10 seconds per test IF
    # you're confident your teardown already cleans up properly.
    "appium:noReset": False,

    # How long Appium waits between commands before killing the session.
    # 120 seconds is generous but safe for slow CI environments.
    "appium:newCommandTimeout": 120,

    # Automatically grant runtime permissions (camera, location, notifications)
    # so we never get a permissions dialog blocking the test.
    "appium:autoGrantPermissions": True,
}


# ── iOS capabilities ───────────────────────────────────────────────────────────
IOS_CAPS = {
    "platformName": "iOS",

    # XCUITest is Apple's native UI testing framework.
    # Appium's XCUITest driver wraps it — same way UiAutomator2 wraps Android's.
    "appium:automationName": "XCUITest",

    "appium:deviceName": _env("IOS_DEVICE_NAME", "iPhone 17 Pro"),
    "appium:platformVersion": _env("IOS_PLATFORM_VERSION", "26.0"),

    # For simulator: path to the .app bundle (a folder, not a file).
    # For physical device: path to the .ipa file.
    "appium:app":             _app_path("IOS_APP_PATH"),

    # bundleId is the iOS equivalent of appPackage — required for XCUITest
    # to identify and launch the app. Find it in the app's Info.plist.
    "appium:bundleId": "com.saucelabs.mydemo.app.ios",

    # noReset: False → reinstall before every session, same as Android.
    # WHY change from True? With True, cart state persists across test runs —
    # items added in one session carry over to the next, breaking count assertions.
    "appium:noReset": False,
    "appium:newCommandTimeout": 120,

    # True = Automatically accept iOS system alert dialogs (push notifications, location, etc.)
    # Same purpose as autoGrantPermissions on Android.
    # I set to False though because iOS displays its login error messages as alerts
    # So I wrote handle_system_alerts() in BasePage for cases where we want it to be handled.
    "appium:autoAcceptAlerts": False,

    # WDA (WebDriverAgent) is the iOS server Appium installs on the device/simulator.
    # On first launch it needs to compile — giving it 2 minutes prevents timeout
    # failures that have nothing to do with your actual tests.
    "appium:wdaLaunchTimeout": 120000,

    # Prevents sims from autocorrecting text input
    "appium:keyboardAutocorrection": False,

    # Sets the keyboard for iOS to never be visible because it covers buttons 
    "appium:connectHardwareKeyboard": True,
}