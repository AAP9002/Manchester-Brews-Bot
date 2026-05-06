from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
import displayio
import time as system_time
from components.TouchButton import TouchButton
from components.WifiIndicator import WifiIndicator
import terminalio
import os
from utils.SendRequest import SendRequest

THANKS_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK = os.getenv("THANKS_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
COFFEE_PARROT_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK = os.getenv("COFFEE_PARROT_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
COFFEE_BLOB_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK = os.getenv("COFFEE_BLOB_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
THANKS_DOG_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK = os.getenv("THANKS_DOG_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
RACHEL_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK = os.getenv("RACHEL_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
LETS_GO_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK = os.getenv("LETS_GO_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
STAR_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK = os.getenv("STAR_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")

class ReactScreen:
    def __init__(self, app_state):
        self.app_state = app_state
        self.screen_group = displayio.Group()
        self.DoneBrewingButton = None
        self.BrewingButton = None
        self.BackButton = None
        self.reactionButtons = []
        self.status_label = None
        self.wifi_indicator = None
        self.build()
        self.setDefaultStatus()

    def goBackToMenu(self):
        self.app_state["current_screen"] = "menu_screen"

    def rebuild(self):
        self.screen_group = displayio.Group()
        self.reactionButtons = []
        self.build()
        self.setDefaultStatus()

    def build(self):
        header = RoundRect(60, 10, 260, 40, 10, fill=0x000000, outline=0xFF00FF, stroke=3)
        self.screen_group.append(header)

        self.BackButton = TouchButton(5, 5, "/images/back.bmp", self.screen_group, self.goBackToMenu, padding=5)

        title = label.Label(terminalio.FONT, text="Send emoji", color=0xFFFFFF)
        title.x = 70
        title.y = 35
        title.scale = 2
        self.screen_group.append(title)

        self.status_label = label.Label(terminalio.FONT, text="", color=0x00FF00)
        self.status_label.x = 5
        self.status_label.y = 225
        self.status_label.scale = 2
        self.screen_group.append(self.status_label)

        self.wifi_indicator = WifiIndicator(266, 222, self.screen_group)

        if self.app_state.get("last_brew_time") is None:
            you_need_to_brew_label = label.Label(terminalio.FONT, text="You must Broadcast a brew", scale=2, color=0xFF0000)
            you_need_to_brew_label.x = 10
            you_need_to_brew_label.y = 120
            self.screen_group.append(you_need_to_brew_label)

            description_label = label.Label(terminalio.FONT, text="to unlock reactions", scale=2, color=0xFF0000)
            description_label.x = 40
            description_label.y = 150
            self.screen_group.append(description_label)
            return

        self.reactionButtons.append(TouchButton(15, 65, "/images/thanks.bmp", self.screen_group, SendRequest.post(THANKS_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK)))
        self.reactionButtons.append(TouchButton(75, 65, "/images/coffee-parrot.bmp", self.screen_group, SendRequest.post(COFFEE_PARROT_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK)))
        self.reactionButtons.append(TouchButton(135, 65, "/images/coffee-blob.bmp", self.screen_group, SendRequest.post(COFFEE_BLOB_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK)))
        self.reactionButtons.append(TouchButton(195, 65, "/images/thanks-dog.bmp", self.screen_group, SendRequest.post(THANKS_DOG_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK)))
        self.reactionButtons.append(TouchButton(255, 65, "/images/rachel.bmp", self.screen_group, SendRequest.post(RACHEL_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK)))
        self.reactionButtons.append(TouchButton(15, 125, "/images/lets-go.bmp", self.screen_group, SendRequest.post(LETS_GO_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK)))
        self.reactionButtons.append(TouchButton(75, 125, "/images/star.bmp", self.screen_group, SendRequest.post(STAR_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK)))

    def showAllEmojisHaveBeenUsedMessage(self):
        self.status_label.text = "All used... Time to brew!"

    def setDefaultStatus(self):
        self.status_label.text = "React to the last brew!"

    def get_screen(self):
        return self.screen_group
    
    def is_button_pressed(self, touch):
        if self.BackButton.isPressed(touch):
            return True
        for button in self.reactionButtons:
            if button.isPressed(touch):
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
        for button in self.reactionButtons:
            if button.isPressed(touch):
                button.runCallback()
                button.hideButton()

        self.status_label.text = "SENT! Great Success!"
        system_time.sleep(2)
        if all(button.hidden for button in self.reactionButtons):
            self.showAllEmojisHaveBeenUsedMessage()
        else:
            self.setDefaultStatus()
        self.goBackToMenu()