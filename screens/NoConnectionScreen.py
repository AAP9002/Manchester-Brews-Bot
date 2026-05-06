# screens/NoConnectionScreen.py
import os
import wifi
import displayio
from adafruit_display_shapes.rect import Rect

from utils import layout
from utils.config import COLOURS, MESSAGES, TIMING, DISPLAY


class NoConnectionScreen:
    def __init__(self, navigator, app_state):
        self._navigator = navigator
        self._state = app_state
        self._next_attempt = 0.0

        self._group = displayio.Group()
        self._group.append(Rect(0, 0, DISPLAY["width"], DISPLAY["height"],
                                fill=COLOURS["dark"]))

        # Single big centred message.
        self._group.append(layout.make_text_label(
            MESSAGES["no_connection"], scale=2, color=COLOURS["red"],
            x="center", y="center",
            parent_width=DISPLAY["width"], parent_height=DISPLAY["height"],
        ))

    # ---------- Navigator protocol ----------

    def get_group(self):
        return self._group

    def on_enter(self, params=None):
        self._next_attempt = 0.0  # try immediately

    def handle_touch(self, touch):
        # No interactive elements; tap does nothing.
        pass

    def tick(self, now):
        # If wifi is already up, leave immediately.
        if wifi.radio.connected:
            self._state["wifi_connected"] = True
            self._navigator.navigate("home")
            return

        if now < self._next_attempt:
            return

        self._next_attempt = now + TIMING["reconnect_poll"]

        ssid = os.getenv("CIRCUITPY_WIFI_SSID")
        password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
        if not ssid or not password:
            return

        try:
            wifi.radio.connect(ssid, password)
        except Exception as exc:
            print("reconnect failed:", exc)
            return

        if wifi.radio.connected:
            self._state["wifi_connected"] = True
            self._navigator.navigate("home")
