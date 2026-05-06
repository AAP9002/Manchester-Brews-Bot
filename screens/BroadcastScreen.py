from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
import displayio
import time as system_time
from components.TouchButton import TouchButton
from components.WifiIndicator import WifiIndicator
import terminalio
import os
from utils.SendRequest import SendRequest

send_message_webhook = os.getenv("SEND_MESSAGE_SLACK_WEBHOOK")

def send_coffee_brewing_message():
    payload = {
        "messageContent": ":coffee-loading:"
    }
    SendRequest.post(send_message_webhook, payload)
        
def send_coffee_made_message():
    payload = {
        "messageContent": ":i-want-to-let-you-know-i-have-recently-made-coffee-but-i-dont-want-to-write-out-a-message:"
    }
    SendRequest.post(send_message_webhook, payload)    

class BroadcastScreen:
    def __init__(self, app_state):
        self.app_state = app_state
        self.screen_group = displayio.Group()
        self.DoneBrewingButton = None
        self.BrewingButton = None
        self.BackButton = None
        self.status_label = None
        self.wifi_indicator = None
        self.build()
        self.setDefaultStatus()

    def goBackToMenu(self):
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

        self.DoneBrewingButton = TouchButton(180, 80, "/images/coffee-done.bmp", self.screen_group, send_coffee_made_message)
        self.BrewingButton = TouchButton(10, 85, "/images/loading.bmp", self.screen_group, send_coffee_brewing_message)

        button_label_done = label.Label(terminalio.FONT, text="Ready!", scale=2, color=0xFFFFFF)
        button_label_done.x = 210
        button_label_done.y = 64
        self.screen_group.append(button_label_done)

        self.wifi_indicator = WifiIndicator(266, 222, self.screen_group)

    def setDefaultStatus(self):
        self.status_label.text = "Press a button to send"

    def get_screen(self):
        return self.screen_group
    
    def is_button_pressed(self, touch):
        if self.DoneBrewingButton.isPressed(touch):
            return True
        elif self.BrewingButton.isPressed(touch):
            return True
        elif self.BackButton.isPressed(touch):
            return True
        return False

    def fire_button_callback(self, touch):
        if self.BackButton.isPressed(touch):
            self.BackButton.runCallback()
            return
        if not self.app_state.get("wifi_connected", False):
            self.status_label.text = "No WiFi connection!"
            self.status_label.color = 0xFF0000
            return
        self.status_label.color = 0x00FF00
        self.status_label.text = "Sending..."
        if self.DoneBrewingButton.isPressed(touch):
            self.app_state["last_brew_time"] = system_time.monotonic()
            self.app_state["reset_react_options"] = True
            self.DoneBrewingButton.runCallback()
        elif self.BrewingButton.isPressed(touch):
            self.app_state["last_brew_time"] = system_time.monotonic()
            self.app_state["reset_react_options"] = True
            self.BrewingButton.runCallback()
        self.status_label.text = "SENT! Great Success!"
        system_time.sleep(2)
        self.setDefaultStatus()
        self.goBackToMenu()