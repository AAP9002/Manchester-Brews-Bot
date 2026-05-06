"""Reusable success / confirmation overlay.

Configured per-navigation via on_enter(params); a single instance is
registered with the Navigator and reused for every successful action.
"""

import time
import displayio
from adafruit_display_shapes.rect import Rect

from utils import layout
from utils.config import COLOURS, TIMING, DISPLAY


class SuccessScreen:
    def __init__(self, navigator):
        self._navigator = navigator
        self._group = displayio.Group()
        self._dismiss_at = 0.0
        self._return_to = "home"

    def get_group(self):
        return self._group

    def on_enter(self, params=None):
        params = params or {}
        message = params.get("message", "Done")
        image_path = params.get("image_path")
        duration = params.get("duration", TIMING["success_dismiss"])
        self._return_to = params.get("return_to", "home")

        # Rebuild the displayio sub-tree from scratch each entry.
        while len(self._group):
            self._group.pop()

        self._group.append(Rect(0, 0, DISPLAY["width"], DISPLAY["height"],
                                fill=COLOURS["success"]))

        # Icon: BMP if provided, otherwise a vector checkmark.
        if image_path:
            try:
                bitmap = displayio.OnDiskBitmap(image_path)
                tile = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
                tile.x = (DISPLAY["width"] - bitmap.width) // 2
                tile.y = 30
                self._group.append(tile)
            except OSError:
                self._draw_checkmark(y=30)
        else:
            self._draw_checkmark(y=30)

        # Message: str (one line, big) or 2-tuple (subtitle small + main bold).
        text_area_top = 110
        if isinstance(message, tuple):
            subtitle, main = message
            self._group.append(layout.make_text_label(
                subtitle, scale=1, color=COLOURS["white"],
                x="center", y=text_area_top,
                parent_width=DISPLAY["width"], parent_height=DISPLAY["height"],
            ))
            self._group.append(layout.make_text_label(
                main, scale=2, color=COLOURS["white"],
                x="center", y=text_area_top + 30,
                parent_width=DISPLAY["width"], parent_height=DISPLAY["height"],
            ))
        else:
            self._group.append(layout.make_text_label(
                message, scale=2, color=COLOURS["white"],
                x="center", y=text_area_top + 30,
                parent_width=DISPLAY["width"], parent_height=DISPLAY["height"],
            ))

        self._dismiss_at = time.monotonic() + duration

    def handle_touch(self, touch):
        # Tapping during the success window dismisses early.
        self._navigator.navigate(self._return_to)

    def tick(self, now):
        if self._dismiss_at and now >= self._dismiss_at:
            self._dismiss_at = 0.0
            self._navigator.navigate(self._return_to)

    def _draw_checkmark(self, y):
        # Compose a tick from small white squares along two diagonals.
        # Centred horizontally on DISPLAY["width"], total tick height ~40 px.
        #
        # Tick anatomy (in local tick-space, origin at top of bounding box):
        #   short stroke: from (0, 22) down-right to (14, 36)
        #   long  stroke: from (14, 36) up-right   to (40, 10)
        # Bounding box ~ 40 wide x 36 tall. Each step plots a 6x6 white square,
        # which gives a ~6 px stroke width.
        cx = DISPLAY["width"] // 2
        tick_w = 40
        left = cx - tick_w // 2  # left edge of tick bounding box
        top = y                  # top of tick bounding box

        stroke = 6
        white = COLOURS["white"]

        # Short stroke: 14 px right, 14 px down.
        for i in range(15):
            px = left + i
            py = top + 22 + i
            self._group.append(Rect(px, py, stroke, stroke, fill=white))

        # Long stroke: 26 px right, 26 px up, starting at the elbow.
        elbow_x = left + 14
        elbow_y = top + 36
        for i in range(27):
            px = elbow_x + i
            py = elbow_y - i
            self._group.append(Rect(px, py, stroke, stroke, fill=white))
