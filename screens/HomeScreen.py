"""Home screen: three card buttons matching the v2 design.

- Send announcement (left half, blue fill) -> navigate("announcement")
- Low on beans (top right, red border)     -> Slack post + navigate("success")
- Log your intake (bottom right, teal border) -> increment counter + navigate("success")
"""

import os
import displayio
from adafruit_display_shapes.rect import Rect

from components.CardButton import CardButton
from utils.config import COLOURS, IMAGES, MESSAGES, DISPLAY
from utils import slack


class HomeScreen:
    def __init__(self, navigator, send, coffee_counter):
        self._navigator = navigator
        self._send = send
        self._counter = coffee_counter

        self._group = displayio.Group()
        self._group.append(Rect(0, 0, DISPLAY["width"], DISPLAY["height"],
                                fill=COLOURS["dark"]))

        pad = 8
        # Layout: left card spans full height; right column split top/bottom.
        left_w = (DISPLAY["width"] - pad * 3) // 2
        right_x = pad + left_w + pad
        right_w = DISPLAY["width"] - right_x - pad
        right_h = (DISPLAY["height"] - pad * 3) // 2

        self._send_card = CardButton(
            group=self._group,
            x=pad, y=pad, width=left_w, height=DISPLAY["height"] - pad * 2,
            icon_path=IMAGES["send_icon"], label=("Send", "announcement"),
            border_colour=COLOURS["blue"], fill_colour=COLOURS["blue"],
            label_scale=1,
            callback=lambda: self._navigator.navigate("announcement"),
        )

        self._low_beans_card = CardButton(
            group=self._group,
            x=right_x, y=pad, width=right_w, height=right_h,
            icon_path=IMAGES["low_beans_icon"], label="Low on beans",
            border_colour=COLOURS["red"], label_colour=COLOURS["red"],
            label_scale=1,
            callback=self._fire_low_beans,
        )

        self._log_intake_card = CardButton(
            group=self._group,
            x=right_x, y=pad + right_h + pad, width=right_w, height=right_h,
            icon_path=IMAGES["log_intake_icon"], label="Log your intake",
            border_colour=COLOURS["teal"], label_colour=COLOURS["teal"],
            label_scale=1,
            callback=self._fire_log_intake,
        )

        self._cards = [self._send_card, self._low_beans_card, self._log_intake_card]

    # ---------- Navigator protocol ----------

    def get_group(self):
        return self._group

    def on_enter(self, params=None):
        # No state to reset; cards keep their resting fill.
        pass

    def handle_touch(self, touch):
        import time as _t
        now = _t.monotonic()
        for card in self._cards:
            if card.is_pressed(touch):
                card.flash(now)
                card.fire()
                return

    def tick(self, now):
        for card in self._cards:
            card.tick(now)

    # ---------- Actions ----------

    def _fire_low_beans(self):
        slack.post(self._send, slack.Msg.LOW_ON_BEANS)  # ignore (ok, body) — success screen always shows

        name = os.getenv("LOW_BEANS_PERSON") or "Someone"
        subtitle_template, main_line = MESSAGES["low_on_beans"]
        formatted = (subtitle_template.format(name=name), main_line)

        self._navigator.navigate("success", {
            "message": formatted,
            "return_to": "home",
        })

    def _fire_log_intake(self):
        self._counter.increment()
        self._counter.sync()
        count = self._counter.get_count()
        cup_word = "cup" if count == 1 else "cups"
        self._navigator.navigate("success", {
            "message": (MESSAGES["log_intake_default"],
                        str(count) + " " + cup_word + " so far"),
            "return_to": "home",
        })
