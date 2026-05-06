"""Announcement screen: Brewing / Ready cards plus a small back button.

Replaces v1's BroadcastScreen and fixes the long-standing
callback-at-construction bug (CardButton.__init__ now raises if a
non-callable is passed; the back-button TouchButton uses a lambda).
"""

import displayio
from adafruit_display_shapes.rect import Rect

from components.CardButton import CardButton
from components.TouchButton import TouchButton
from utils.config import COLOURS, IMAGES, MESSAGES, DISPLAY
from utils import slack


class AnnouncementScreen:
    def __init__(self, navigator, send):
        self._navigator = navigator
        self._send = send

        self._group = displayio.Group()
        self._group.append(Rect(0, 0, DISPLAY["width"], DISPLAY["height"],
                                fill=COLOURS["dark"]))

        pad = 8
        back_btn_size = 32  # match back.bmp dimensions

        card_h = DISPLAY["height"] - pad * 2
        card_w = (DISPLAY["width"] - pad * 3) // 2

        self._brewing_card = CardButton(
            group=self._group,
            x=pad, y=pad, width=card_w, height=card_h,
            icon_path=IMAGES["brewing_icon"], label="Brewing",
            border_colour=COLOURS["blue"],
            callback=self._fire_brewing,
        )

        self._ready_card = CardButton(
            group=self._group,
            x=pad + card_w + pad, y=pad, width=card_w, height=card_h,
            icon_path=IMAGES["ready_icon"], label="Ready",
            border_colour=COLOURS["blue"],
            callback=self._fire_ready,
        )

        # Back button overlays the bottom-right area of the right card.
        back_x = DISPLAY["width"] - pad - back_btn_size
        back_y = DISPLAY["height"] - pad - back_btn_size
        self._back_btn = TouchButton(
            x=back_x, y=back_y,
            image_path=IMAGES["back_icon"],
            display_group=self._group,
            callback=lambda: self._navigator.navigate("home"),
            padding=8,
            transparent_color=0x000000,
        )

        self._cards = [self._brewing_card, self._ready_card]

    # ---------- Navigator protocol ----------

    def get_group(self):
        return self._group

    def on_enter(self, params=None):
        pass

    def handle_touch(self, touch):
        import time as _t
        now = _t.monotonic()
        # Back button takes priority — it sits visually on top of a card.
        if self._back_btn.isPressed(touch):
            self._back_btn.runCallback()
            return
        for card in self._cards:
            if card.is_pressed(touch):
                card.flash(now)
                card.fire()
                return

    def tick(self, now):
        for card in self._cards:
            card.tick(now)

    # ---------- Actions ----------

    def _fire_brewing(self):
        slack.post(self._send, slack.Msg.BREWING)
        self._navigator.navigate("success", {
            "message": MESSAGES["brewing"],
            "image_path": IMAGES["brewing_icon"],
            "return_to": "home",
        })

    def _fire_ready(self):
        slack.post(self._send, slack.Msg.READY)
        self._navigator.navigate("success", {
            "message": MESSAGES["ready"],
            "image_path": IMAGES["ready_icon"],
            "return_to": "home",
        })
