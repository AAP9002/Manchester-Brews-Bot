from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
import displayio
import time as system_time
from components.TouchButton import TouchButton
from components.WifiIndicator import WifiIndicator
import terminalio
import os
from utils.config import IMAGES

send_message_webhook = os.getenv("SEND_MESSAGE_SLACK_WEBHOOK")

class BroadcastScreen:
    def __init__(self, app_state, send_request, navigator=None):
        self.app_state = app_state
        self._send = send_request
        self._navigator = navigator
        self.screen_group = displayio.Group()
        self.DoneBrewingButton = None
        self.BrewingButton = None
        self.BackButton = None
        self.status_label = None
        self.wifi_indicator = None
        self.build()
        self.setDefaultStatus()

    def send_coffee_brewing_message(self):
        # SMOKE TEST P4.1: navigate to SuccessScreen with brewing BMP.
        if self._navigator is None:
            return
        self._navigator.navigate("success", {
            "message": "Brewing announced",
            "image_path": IMAGES["brewing_icon"],
            "return_to": "menu",
        })

    def send_coffee_made_message(self):
        # SMOKE TEST P4.1: navigate to SuccessScreen with ready BMP.
        if self._navigator is None:
            return
        self._navigator.navigate("success", {
            "message": "Ready announced",
            "image_path": IMAGES["ready_icon"],
            "return_to": "menu",
        })

    def goBackToMenu(self):
        if self._navigator is not None:
            self._navigator.navigate("menu")
        else:
            self.app_state["current_screen"] = "menu_screen"

    def build(self):
        header = RoundRect(60, 10, 260, 40, 10, fill=0x000000, outline=0xFF00FF, stroke=3)
        self.screen_group.append(header)

        self.BackButton = TouchButton(5, 5, "/images/back.bmp", self.screen_group, self.goBackToMenu, padding=5)

        title = label.Label(terminalio.FONT, text="Make announcement", color=0xFFFFFF)
        title.x = 70
        title.y = 35
        title.scale = 2
        self.screen_group.append(title)

        self.status_label = label.Label(terminalio.FONT, text="", color=0x00FF00)
        self.status_label.x = 5
        self.status_label.y = 225
        self.status_label.scale = 2
        self.screen_group.append(self.status_label)

        button_label = label.Label(terminalio.FONT, text="Brewing", scale=2, color=0xFFFFFF)
        button_label.x = 30
        button_label.y = 65
        self.screen_group.append(button_label)

        self.DoneBrewingButton = TouchButton(180, 80, "/images/coffee-done.bmp", self.screen_group, self.send_coffee_made_message)
        self.BrewingButton = TouchButton(10, 85, "/images/loading.bmp", self.screen_group, self.send_coffee_brewing_message)

        button_label_done = label.Label(terminalio.FONT, text="Ready!", scale=2, color=0xFFFFFF)
        button_label_done.x = 210
        button_label_done.y = 64
        self.screen_group.append(button_label_done)

        self.wifi_indicator = WifiIndicator(266, 222, self.screen_group)

    def setDefaultStatus(self):
        self.status_label.text = "Press a button to send"

    def get_screen(self):
        return self.screen_group

    # ---------- Navigator protocol ----------

    def get_group(self):
        return self.screen_group

    def on_enter(self, params=None):
        self.setDefaultStatus()
        if self.wifi_indicator is not None:
            self.wifi_indicator.update()

    def handle_touch(self, touch):
        # touch is already normalized (tx, ty) by TouchTracker.
        if self.is_button_pressed(touch):
            self.fire_button_callback(touch)

    def tick(self, now):
        # No time-based behaviour for v1 broadcast screen.
        pass

    def is_button_pressed(self, touch):
        if self.DoneBrewingButton.isPressed(touch):
            return True
        elif self.BrewingButton.isPressed(touch):
            return True
        elif self.BackButton.isPressed(touch):
            return True
        return False

    def fire_button_callback(self, touch):
        # SMOKE TEST P4.1: brewing/done callbacks navigate to SuccessScreen
        # themselves; skip the v1 trailing sleep+goBackToMenu so SuccessScreen
        # isn't pre-empted.
        if self.BackButton.isPressed(touch):
            self.BackButton.runCallback()
            return
        if self.DoneBrewingButton.isPressed(touch):
            self.app_state["last_brew_time"] = system_time.monotonic()
            self.DoneBrewingButton.runCallback()
            return
        if self.BrewingButton.isPressed(touch):
            self.app_state["last_brew_time"] = system_time.monotonic()
            self.BrewingButton.runCallback()
            return