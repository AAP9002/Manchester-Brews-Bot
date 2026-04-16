from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
import displayio
import time as system_time
from components.TouchButton import TouchButton
from components.WifiIndicator import WifiIndicator
import terminalio
import random
import os
import microcontroller
from utils.CoffeeCounter import CoffeeCounter
from utils.SendRequest import SendRequest

class MenuScreen:
    def __init__(self, app_state):
        self.app_state = app_state
        self.screen_group = displayio.Group()
        self.BroadcastButton = None
        self.PlusOneButton = None
        self.status_label = None
        self.temp_label = None
        self.weather_label = None
        self.rain_label = None
        self.count_label = None
        self.wifi_indicator = None
        self.last_plus_one_time = 0
        self.last_low_beans_time = 0
        self.plus_btn_bg = None
        self.plus_btn_label = None
        self.bean_btn_bg = None
        self.bean_btn_icon = None
        self.bean_btn_label = None
        self.bean_btn_label2 = None
        self.bean_btn_bounds = None
        self.header_border = None
        self.coffee_box = None
        self.build()
        self.setDefaultStatus()

    def openBroadcastScreen(self):
        self.app_state["current_screen"] = "broadcast_screen"

    def incrementCoffeeCount(self):
        CoffeeCounter.increment()
        self.updateCoffeeCount()
        self.plus_btn_bg.fill = 0x444444
        self.plus_btn_bg.outline = 0x666666
        self.plus_btn_label.color = 0x888888
        self.celebrateCount()
        CoffeeCounter.sync()
        self.updateCoffeeCount()
        self.plus_btn_bg.fill = 0xFF8C00
        self.plus_btn_bg.outline = 0xFFAA33
        self.plus_btn_label.color = 0xFFFFFF

    def celebrateCount(self):
        original_color = self.count_label.color
        original_scale = self.count_label.scale
        messages = [
            "Whoop Get Caffeinated!",
            "Caffeine logged!",
            "Another Cup Conquered!",
            "Bean There, Brewed That!",
            "Brew-tiful! Stay Wired!",
            "Fuel Up! Cup Logged!",
            "Soft-Caffine-Wire!",
            "Mr beans is proud",
            "Sip sip hooray!",
            "Brew-lliant work!",
            "That's the good stuff!",
            "Espresso yourself!",
        ]
        self.status_label.text = random.choice(messages)
        rainbow = [0xFF0000, 0xFF7700, 0xFFFF00, 0x00FF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF]
        border_colors = [0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF, 0xFF00FF, 0xFF8C00, 0xFFFFFF]
        self.count_label.scale = 5
        for i in range(len(rainbow)):
            self.count_label.color = rainbow[i]
            self.status_label.color = rainbow[i]
            self.header_border.outline = border_colors[i]
            self.coffee_box.outline = border_colors[(i + 3) % len(border_colors)]
            system_time.sleep(0.1)
        self.count_label.scale = 3
        for i in range(len(rainbow)):
            self.count_label.color = rainbow[len(rainbow) - 1 - i]
            self.status_label.color = rainbow[len(rainbow) - 1 - i]
            self.header_border.outline = border_colors[len(border_colors) - 1 - i]
            self.coffee_box.outline = border_colors[(len(border_colors) - 1 - i + 3) % len(border_colors)]
            system_time.sleep(0.1)
        self.count_label.scale = original_scale
        self.count_label.color = original_color
        self.status_label.color = 0x00FF00
        self.header_border.outline = 0xFF00FF
        self.coffee_box.outline = 0xFF8C00
        system_time.sleep(0.5)

    def build(self):
        self.header_border = RoundRect(10, 10, 300, 40, 10, fill=0x000000, outline=0xFF00FF, stroke=3)
        self.screen_group.append(self.header_border)

        title = label.Label(terminalio.FONT, text="Manchester-Brews   c|_|", color=0xFFFFFF)
        title.x = 25
        title.y = 35
        title.scale = 2
        self.screen_group.append(title)

        self.status_label = label.Label(terminalio.FONT, text="", color=0x00FF00)
        self.status_label.x = 5
        self.status_label.y = 225
        self.status_label.scale = 2
        self.screen_group.append(self.status_label)

        button_label = label.Label(terminalio.FONT, text="Broadcast", scale=2, color=0xFFFFFF)
        button_label.x = 30
        button_label.y = 65
        self.screen_group.append(button_label)

        self.BroadcastButton = TouchButton(25, 85, "/images/broadcast.bmp", self.screen_group, self.openBroadcastScreen)

        weather_bg = RoundRect(160, 58, 90, 60, 8, fill=0x001830, outline=0x2266AA, stroke=2)
        self.screen_group.append(weather_bg)

        self.temp_label = label.Label(terminalio.FONT, text="", scale=2, color=0xFFFF00)
        self.temp_label.x = 165
        self.temp_label.y = 74
        self.screen_group.append(self.temp_label)

        self.weather_label = label.Label(terminalio.FONT, text="", scale=1, color=0xADD8E6)
        self.weather_label.x = 165
        self.weather_label.y = 91
        self.screen_group.append(self.weather_label)

        self.rain_label = label.Label(terminalio.FONT, text="", scale=1, color=0x87CEEB)
        self.rain_label.x = 165
        self.rain_label.y = 104
        self.screen_group.append(self.rain_label)

        bean_btn_x = 255
        bean_btn_y = 58
        bean_btn_w = 60
        bean_btn_h = 60
        self.bean_btn_bounds = (bean_btn_x, bean_btn_y, bean_btn_w, bean_btn_h)
        self.bean_btn_bg = RoundRect(bean_btn_x, bean_btn_y, bean_btn_w, bean_btn_h, 6, fill=0x8B0000, outline=0xFF3333, stroke=2)
        self.screen_group.append(self.bean_btn_bg)
        self.bean_btn_icon = label.Label(terminalio.FONT, text="!", scale=2, color=0xFFFF00)
        self.bean_btn_icon.anchor_point = (0.5, 0.0)
        self.bean_btn_icon.anchored_position = (bean_btn_x + bean_btn_w // 2, bean_btn_y + 6)
        self.screen_group.append(self.bean_btn_icon)
        self.bean_btn_label = label.Label(terminalio.FONT, text="Send Low", scale=1, color=0xFFFFFF)
        self.bean_btn_label.anchor_point = (0.5, 0.0)
        self.bean_btn_label.anchored_position = (bean_btn_x + bean_btn_w // 2, bean_btn_y + 32)
        self.screen_group.append(self.bean_btn_label)
        self.bean_btn_label2 = label.Label(terminalio.FONT, text="Beans", scale=1, color=0xFFFFFF)
        self.bean_btn_label2.anchor_point = (0.5, 0.0)
        self.bean_btn_label2.anchored_position = (bean_btn_x + bean_btn_w // 2, bean_btn_y + 43)
        self.screen_group.append(self.bean_btn_label2)

        self.coffee_box = RoundRect(160, 125, 155, 80, 8, fill=0x120800, outline=0xFF8C00, stroke=2)
        self.screen_group.append(self.coffee_box)

        year_label = label.Label(terminalio.FONT, text="Brews this year", scale=1, color=0xAAAAAA)
        year_label.x = 168
        year_label.y = 140
        self.screen_group.append(year_label)

        self.count_label = label.Label(terminalio.FONT, text="", scale=3, color=0x00FF00)
        self.count_label.anchor_point = (0.5, 0.5)
        self.count_label.anchored_position = (240, 167)
        self.screen_group.append(self.count_label)

        plus_btn_x = 160
        plus_btn_y = 186
        plus_btn_w = 155
        plus_btn_h = 26
        self.plus_btn_bounds = (plus_btn_x, plus_btn_y, plus_btn_w, plus_btn_h)
        self.plus_btn_bg = RoundRect(plus_btn_x, plus_btn_y, plus_btn_w, plus_btn_h, 8, fill=0xFF8C00, outline=0xFFAA33, stroke=2)
        self.screen_group.append(self.plus_btn_bg)
        self.plus_btn_label = label.Label(terminalio.FONT, text="Log Brew +", scale=2, color=0xFFFFFF)
        self.plus_btn_label.x = plus_btn_x + 23
        self.plus_btn_label.y = plus_btn_y + plus_btn_h // 2
        self.screen_group.append(self.plus_btn_label)

        self.wifi_indicator = WifiIndicator(266, 222, self.screen_group)

    def setDefaultStatus(self):
        if self.app_state["last_brew_time"]:
            elapsed = int(system_time.monotonic() - self.app_state["last_brew_time"])
            hour = elapsed // 3600
            minutes = elapsed // 60
            seconds = elapsed % 60
            if hour > 0:
                self.status_label.text = f"Last Brewed: {hour}h {minutes%60}m ago"
            else:
                self.status_label.text = f"Last Brewed: {minutes}m {seconds}s ago"
        else:
            self.status_label.text = "Last Brewed: Not yet..."

    def updateStatus(self):
        self.setDefaultStatus()
        self.updateWeather()
        self.updateCoffeeCount()

    def get_screen(self):
        return self.screen_group
    
    def updateWeather(self):
        temp = self.app_state.get("weather_temp", None)
        condition = self.app_state.get("weather_condition", None)
        rain = self.app_state.get("weather_rain_chance", None)
        if temp is not None and condition is not None:
            self.temp_label.text = str(round(temp, 1)) + "C"
            self.weather_label.text = condition
            self.rain_label.text = ("Rain: " + str(rain) + "%") if rain is not None else ""
        else:
            self.temp_label.text = ""
            self.weather_label.text = "No weather"
            self.rain_label.text = ""

    def updateCoffeeCount(self):
        count = self.app_state.get("coffee_count", 0)
        self.count_label.text = str(count)

    def isLowBeansPressed(self, touch):
        raw_x, raw_y = touch["x"], touch["y"]
        tx = raw_y
        ty = 240 - raw_x
        bx, by, bw, bh = self.bean_btn_bounds
        pad = 8
        return (bx - pad) <= tx <= (bx + bw + pad) and (by - pad) <= ty <= (by + bh + pad)

    def sendLowBeansAlert(self):
        webhook = os.getenv("SEND_MESSAGE_SLACK_WEBHOOK")
        if not webhook:
            self.status_label.text = "No webhook set!"
            self.status_label.color = 0xFF0000
            return
        self.bean_btn_bg.fill = 0x440000
        self.bean_btn_icon.color = 0x666600
        self.bean_btn_label.color = 0x888888
        self.bean_btn_label2.color = 0x888888
        self.status_label.color = 0xFF6666
        self.status_label.text = "Sending bean alert..."
        bean_emoji = random.choice([":bean:", ":noot_like_this:", ":comfy-panic:", ":dont-panic:"])
        payload = {"messageContent": bean_emoji + " Running low on coffee beans!"}
        try:
            SendRequest.post(webhook, payload)
            self.status_label.text = "Bean alert sent!"
        except Exception as e:
            self.status_label.text = "Send failed!"
        self.bean_btn_bg.fill = 0x8B0000
        self.bean_btn_icon.color = 0xFFFF00
        self.bean_btn_label.color = 0xFFFFFF
        self.bean_btn_label2.color = 0xFFFFFF
        self.status_label.color = 0x00FF00
        system_time.sleep(1.5)

    def isPlusOnePressed(self, touch):
        raw_x, raw_y = touch["x"], touch["y"]
        tx = raw_y
        ty = 240 - raw_x
        bx, by, bw, bh = self.plus_btn_bounds
        pad = 10
        return (bx - pad) <= tx <= (bx + bw + pad) and (by - pad) <= ty <= (by + bh + pad)

    def is_button_pressed(self, touch):
        if self.BroadcastButton.isPressed(touch):
            return True
        elif self.isPlusOnePressed(touch):
            return True
        elif self.isLowBeansPressed(touch):
            return True
        return False

    def fire_button_callback(self, touch):
        if self.BroadcastButton.isPressed(touch):
            self.BroadcastButton.runCallback()
        elif self.isPlusOnePressed(touch):
            if not self.app_state.get("wifi_connected", False):
                self.status_label.text = "No WiFi connection!"
                self.status_label.color = 0xFF0000
            else:
                now = system_time.monotonic()
                if now - self.last_plus_one_time >= 1.5:
                    self.last_plus_one_time = now
                    self.incrementCoffeeCount()
        elif self.isLowBeansPressed(touch):
            now = system_time.monotonic()
            if now - self.last_low_beans_time >= 3.0:
                self.last_low_beans_time = now
                if not self.app_state.get("wifi_connected", False):
                    self.status_label.text = "No WiFi connection!"
                    self.status_label.color = 0xFF0000
                else:
                    self.sendLowBeansAlert()
        self.setDefaultStatus()
