import os
import time as system_time

import board
import displayio
import wifi

import adafruit_cst8xx

from utils.Navigator import Navigator
from utils.touch import TouchTracker
from utils.SendRequest import SendRequest
from utils.CoffeeCounter import CoffeeCounter
from utils.config import TIMING

from screens.HomeScreen import HomeScreen
from screens.AnnouncementScreen import AnnouncementScreen
from screens.SuccessScreen import SuccessScreen
from screens.NoConnectionScreen import NoConnectionScreen


def connect_wifi():
    try:
        wifi.radio.connect(
            os.getenv("CIRCUITPY_WIFI_SSID"),
            os.getenv("CIRCUITPY_WIFI_PASSWORD"),
        )
        return True
    except Exception as exc:
        print("initial wifi connect failed:", exc)
        return False


app_state = {
    "wifi_connected": connect_wifi(),
    "coffee_count": 0,
    "last_brew_time": None,
}

display = board.DISPLAY
ctp = adafruit_cst8xx.Adafruit_CST8XX(board.I2C())

send = SendRequest(app_state)
counter = CoffeeCounter(send, app_state)

navigator = Navigator(display)
navigator.register("home",          HomeScreen(navigator, send, counter))
navigator.register("announcement",  AnnouncementScreen(navigator, send))
navigator.register("success",       SuccessScreen(navigator))
navigator.register("no_connection", NoConnectionScreen(navigator, app_state))

navigator.navigate("home")
counter.fetch()  # initial coffee count

tracker = TouchTracker(ctp)
last_wifi_check = 0.0

while True:
    touch = tracker.poll()
    if touch is not None:
        navigator.handle_touch(touch)

    now = system_time.monotonic()

    if now - last_wifi_check > TIMING["wifi_poll"]:
        last_wifi_check = now
        connected = wifi.radio.connected
        app_state["wifi_connected"] = connected
        if not connected and navigator.active_name != "no_connection":
            navigator.navigate("no_connection")

    navigator.tick(now)
