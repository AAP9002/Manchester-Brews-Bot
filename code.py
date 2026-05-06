import os
import time as system_time
import wifi
import board
import adafruit_cst8xx
from screens.BroadcastScreen import BroadcastScreen
from screens.MenuScreen import MenuScreen
from screens.SuccessScreen import SuccessScreen
from screens.NoConnectionScreen import NoConnectionScreen
# from screens.ReactScreen import ReactScreen
from utils.SendRequest import SendRequest
from utils.CoffeeCounter import CoffeeCounter
from utils.Navigator import Navigator
from utils.touch import TouchTracker
from utils.config import TIMING

# Shared state for screen switching
app_state = {
    "last_brew_time": None,
    "reset_react_options": False,
    "wifi_connected": False,
    "coffee_count": 0,
    }

display = board.DISPLAY
ctp = adafruit_cst8xx.Adafruit_CST8XX(board.I2C())

ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

thank_you_react_webhook = os.getenv("THANKS_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
coffee_parrot_react_webhook = os.getenv("COFFEE_PARROT_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")

print(f"\nConnecting to {ssid}...")
try:
    wifi.radio.connect(ssid, password)
    app_state["wifi_connected"] = True
    print("WiFi Connected!")
except Exception as e:
    print(f"WiFi Error: {e}")

send_request = SendRequest(app_state)
coffee_counter = CoffeeCounter(send_request, app_state)

# ------------------- Build UI Once -------------------
navigator = Navigator(display)
menu_screen = MenuScreen(app_state, send_request, coffee_counter, navigator=navigator)
broadcast_screen = BroadcastScreen(app_state, send_request, navigator=navigator)
success_screen = SuccessScreen(navigator)
no_connection_screen = NoConnectionScreen(navigator, app_state)
# react_screen = ReactScreen(app_state)

navigator.register("menu", menu_screen)
navigator.register("broadcast", broadcast_screen)
navigator.register("success", success_screen)
navigator.register("no_connection", no_connection_screen)
# SMOKE TEST: NoConnectionScreen.tick navigates to "home" on reconnect; alias menu under "home" until P4.2 lands.
navigator.register("home", menu_screen)
navigator.navigate("menu")

# Fetch coffee count from Google Sheets
if app_state["wifi_connected"]:
    coffee_counter.fetch()
    menu_screen.updateCoffeeCount()

# ------------------- Main Loop -------------------
tracker = TouchTracker(ctp)
last_wifi_update = 0

while True:
    touch = tracker.poll()
    if touch is not None:
        navigator.handle_touch(touch)

    now = system_time.monotonic()
    navigator.tick(now)

    # Update WiFi strength indicator and reconnect if needed
    if now - last_wifi_update >= TIMING["wifi_poll"]:
        last_wifi_update = now
        active = navigator.active
        if active is not None and getattr(active, "wifi_indicator", None) is not None:
            active.wifi_indicator.update()

        # SMOKE TEST: hand WiFi-drop handling to NoConnectionScreen.
        app_state["wifi_connected"] = wifi.radio.ap_info is not None
        if not app_state["wifi_connected"] and navigator.active_name != "no_connection":
            print("WiFi lost, navigating to NoConnectionScreen...")
            navigator.navigate("no_connection")

    system_time.sleep(0.0001)
