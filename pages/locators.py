from appium.webdriver.common.appiumby import AppiumBy

Locator = tuple


class Nav:
    HAMBURGER_ANDROID  = (AppiumBy.ACCESSIBILITY_ID, "View menu")
    LOGIN_MENU_ANDROID = (AppiumBy.ACCESSIBILITY_ID, "Login Menu Item")
    MORE_TAB_IOS       = (AppiumBy.ACCESSIBILITY_ID, "More-tab-item")
    LOGIN_MENU_IOS     = (AppiumBy.ACCESSIBILITY_ID, "Login Button")
    LOGOUT_IOS         = (AppiumBy.ACCESSIBILITY_ID, "LogOut-menu-item")
    LOGOUT_ANDROID     = (AppiumBy.ACCESSIBILITY_ID, "Logout Menu Item")
    CATALOG_TAB_IOS    = (AppiumBy.ACCESSIBILITY_ID, "Catalog-tab-item")

    # Android: "View cart" confirmed via adb dump on products screen.
    # iOS: "Cart-tab-item" confirmed via ios_dump.py.
    CART_ANDROID = (AppiumBy.ACCESSIBILITY_ID, "View cart")
    CART_IOS     = (AppiumBy.ACCESSIBILITY_ID, "Cart-tab-item")


class LoginLocators:
    # Android — resource-id based (no accessibility IDs on these fields)
    USERNAME_ANDROID           = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/nameET")
    PASSWORD_ANDROID           = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/passwordET")
    LOGIN_BTN_ANDROID          = (AppiumBy.ACCESSIBILITY_ID, "Tap to login with given credentials")
    ERROR_MSG_ANDROID_USERNAME = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/nameErrorTV")
    ERROR_MSG_ANDROID_PASSWORD = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/passwordErrorTV")

    # iOS — located by element type (no accessibility IDs set by devs)
    USERNAME_IOS    = (AppiumBy.XPATH, "//XCUIElementTypeTextField")
    PASSWORD_IOS    = (AppiumBy.XPATH, "//XCUIElementTypeSecureTextField")
    LOGIN_BTN_IOS   = (AppiumBy.ACCESSIBILITY_ID, "Login")
    LOGOUT_MENU_IOS = (AppiumBy.ACCESSIBILITY_ID, "LogOut-menu-item")
    ERROR_MSG       = (AppiumBy.ACCESSIBILITY_ID, "generic-error-message")  # iOS


class ProductsLocators:
    # Android: productTV confirmed via adb dump.
    HEADER_ANDROID = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productTV")
    # iOS: "title" confirmed via ios_dump.py.
    HEADER_IOS     = (AppiumBy.ACCESSIBILITY_ID, "title")

    # Android: productIV is the only clickable element on each card — confirmed
    # via adb dump (clickable="true"). titleTV has clickable="false".
    FIRST_PRODUCT_ANDROID = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productIV")
    # iOS: "Product Image" confirmed via ios_dump.py.
    FIRST_PRODUCT_IOS     = (AppiumBy.ACCESSIBILITY_ID, "Product Image")


class ProductDetailLocators:
    # Android: productTV confirmed via adb dump on detail screen.
    PRODUCT_TITLE_ANDROID = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productTV")
    # iOS: no stable accessibility ID — the element's name is the actual product
    # name (e.g. "Sauce Labs Backpack - Black"), which changes per product.
    # The product name is always the second StaticText on the detail screen:
    # [0] = "Products" (nav label), [1] = product name, [2] = "Price".
    PRODUCT_TITLE_IOS     = (AppiumBy.XPATH, "(//XCUIElementTypeStaticText)[2]")

    # Android: content-desc confirmed via adb dump.
    ADD_TO_CART_ANDROID = (AppiumBy.ACCESSIBILITY_ID, "Tap to add product to cart")
    # iOS: "AddToCart" confirmed via ios_dump.py.
    ADD_TO_CART_IOS     = (AppiumBy.ACCESSIBILITY_ID, "AddToCart")

    # Android: cartTV confirmed via adb dump — only present in tree when count > 0.
    CART_BADGE_ANDROID = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/cartTV")
    # iOS: the cart badge count is not exposed as a separate accessible element.
    # get_cart_badge_count() returns 0 when not found, so assert_cart_badge_count
    # is skipped on iOS in ProductDetailPage.
    CART_BADGE_IOS     = None


class CartLocators:
    # Android: productRV (RecyclerView) presence confirms cart screen loaded.
    CART_SCREEN_ANDROID = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productRV")
    # iOS: "My Cart" confirmed via ios_dump.py.
    CART_SCREEN_IOS     = (AppiumBy.ACCESSIBILITY_ID, "My Cart")

    # Android: cartCL is the ConstraintLayout wrapping each line-item row —
    # confirmed via adb dump resource IDs.
    CART_ITEMS_ANDROID  = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/cartCL")
    # iOS: no cart item container ID — count via item name elements instead.
    CART_ITEMS_IOS      = (AppiumBy.XPATH, "(//XCUIElementTypeStaticText)[2]")

    # Android: titleTV is the product name label within each cart row.
    ITEM_NAME_ANDROID   = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/titleTV")
    # iOS: no stable ID — product name is the second StaticText after "My Cart".
    ITEM_NAME_IOS       = (AppiumBy.XPATH, "(//XCUIElementTypeStaticText)[2]")

    # Android: noTV is the quantity number TextView within each cart row.
    ITEM_QTY_ANDROID    = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/noTV")
    # iOS: the quantity StaticText's accessibility ID is the number itself
    # (e.g. '1', '2'). It's the only StaticText on the cart screen whose name
    # is purely numeric — confirmed via ios_dump.py cart output where '1' appeared
    # as a standalone StaticText after the stepper buttons, not as a sibling.
    # translate() strips all digits — if the result is empty, the name was numeric.
    ITEM_QTY_IOS        = (AppiumBy.XPATH,
                           "//XCUIElementTypeStaticText"
                           "[translate(@name,'0123456789','')='']")