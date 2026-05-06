import os
import time as system_time
import wifi
import board
import adafruit_cst8xx
from screens.BroadcastScreen import BroadcastScreen
from screens.MenuScreen import MenuScreen
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
# react_screen = ReactScreen(app_state)

navigator.register("menu", menu_screen)
navigator.register("broadcast", broadcast_screen)
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

        # Update WiFi state and auto-reconnect if dropped
        app_state["wifi_connected"] = wifi.radio.ap_info is not None
        if not app_state["wifi_connected"]:
            print("WiFi lost, attempting reconnect...")
            try:
                wifi.radio.connect(ssid, password)
                app_state["wifi_connected"] = True
                print("WiFi reconnected!")
                coffee_counter.fetch()
                menu_screen.updateCoffeeCount()
            except Exception as e:
                print("WiFi reconnect failed: " + str(e))

    system_time.sleep(0.0001)
