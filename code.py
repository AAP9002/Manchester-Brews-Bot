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
from utils.WeatherManager import WeatherManager

# Shared state for screen switching
app_state = {
    "current_screen": "menu_screen",
    "last_brew_time": None,
    "reset_react_options": False,
    "wifi_connected": False,
    "coffee_count": 0,
    "weather_temp": None,
    "weather_condition": None,
    "weather_rain_chance": None
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

SendRequest.app_state = app_state
CoffeeCounter.app_state = app_state
WeatherManager.app_state = app_state

# ------------------- Build UI Once -------------------
menu_screen = MenuScreen(app_state)
broadcast_screen = BroadcastScreen(app_state)
# react_screen = ReactScreen(app_state)
display.root_group = menu_screen.get_screen()

# Fetch coffee count from Google Sheets
if app_state["wifi_connected"]:
    CoffeeCounter.fetch()
    menu_screen.updateCoffeeCount()
    WeatherManager.fetch()
    menu_screen.updateWeather()

# ------------------- Main Loop -------------------
last_screen = app_state["current_screen"]
last_wifi_update = 0
last_weather_update = 0

while True:
    touches = ctp.touches
    if touches and len(touches) > 0:
        touch = touches[0]
        if app_state["current_screen"] == "menu_screen" and menu_screen.is_button_pressed(touch):
            menu_screen.fire_button_callback(touch)
        elif app_state["current_screen"] == "broadcast_screen" and broadcast_screen.is_button_pressed(touch):
            broadcast_screen.fire_button_callback(touch)
        # elif app_state["current_screen"] == "react_screen" and react_screen.is_button_pressed(touch):
        #     react_screen.fire_button_callback(touch)

        # if app_state["reset_react_options"]:
        #     react_screen.rebuild()
        #     app_state["reset_react_options"] = False

    # Handle screen switching
    if app_state["current_screen"] != last_screen:
        last_screen = app_state["current_screen"]
        if app_state["current_screen"] == "menu_screen":
            display.root_group = menu_screen.get_screen()
            menu_screen.wifi_indicator.update()
        elif app_state["current_screen"] == "broadcast_screen":
            display.root_group = broadcast_screen.get_screen()
            broadcast_screen.wifi_indicator.update()
        # elif app_state["current_screen"] == "react_screen":
        #     display.root_group = react_screen.get_screen()
        #     react_screen.wifi_indicator.update()
        system_time.sleep(0.5)

    # Update status on menu screen
    if app_state["current_screen"] == "menu_screen":
        menu_screen.updateStatus()

    # Update WiFi strength indicator and reconnect if needed
    if system_time.monotonic() - last_wifi_update >= 5:
        last_wifi_update = system_time.monotonic()
        if app_state["current_screen"] == "menu_screen":
            menu_screen.wifi_indicator.update()
        elif app_state["current_screen"] == "broadcast_screen":
            broadcast_screen.wifi_indicator.update()
        # elif app_state["current_screen"] == "react_screen" and react_screen.wifi_indicator:
        #     react_screen.wifi_indicator.update()

        # Refresh weather every 10 minutes
        if system_time.monotonic() - last_weather_update >= 600:
            last_weather_update = system_time.monotonic()
            WeatherManager.fetch()
            if app_state["current_screen"] == "menu_screen":
                menu_screen.updateWeather()

        # Update WiFi state and auto-reconnect if dropped
        app_state["wifi_connected"] = wifi.radio.ap_info is not None
        if not app_state["wifi_connected"]:
            print("WiFi lost, attempting reconnect...")
            try:
                wifi.radio.connect(ssid, password)
                app_state["wifi_connected"] = True
                print("WiFi reconnected!")
                CoffeeCounter.fetch()
                menu_screen.updateCoffeeCount()
                WeatherManager.fetch()
                menu_screen.updateWeather()
                last_weather_update = system_time.monotonic()
            except Exception as e:
                print("WiFi reconnect failed: " + str(e))

    system_time.sleep(0.0001)
