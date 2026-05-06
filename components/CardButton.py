"""Primary v2 button: BMP icon + label + coloured border in a rounded card.

Usage:
    btn = CardButton(
        group=parent_group,
        x=10, y=20, width=140, height=200,
        icon_path=IMAGES["send_icon"],
        label="Send announcement",
        border_colour=COLOURS["blue"],
        fill_colour=COLOURS["blue"],   # optional; None = dark fill
        callback=lambda: navigator.navigate("announcement"),
    )

    # In the screen's handle_touch:
    if btn.is_pressed(touch):
        btn.flash(now)
        btn.fire()

    # In the screen's tick:
    btn.tick(now)
"""

import displayio
from adafruit_display_shapes.roundrect import RoundRect

from utils import layout
from utils.config import COLOURS, TIMING


CARD_RADIUS = 12
CARD_BORDER_WIDTH = 3
DEFAULT_FLASH_DURATION = 0.18


class CardButton:
    def __init__(self, group, x, y, width, height,
                 icon_path, label, border_colour,
                 callback, fill_colour=None,
                 label_colour=None, label_scale=2, hidden=False):
        if not callable(callback):
            raise TypeError("CardButton callback must be callable; wrap with lambda")

        self._x = x
        self._y = y
        self._w = width
        self._h = height
        self._callback = callback
        self._hidden = hidden
        self._flash_until = 0.0
        self._next_fire_at = 0.0

        self._resting_fill = fill_colour if fill_colour is not None else COLOURS["dark"]
        self._flash_fill = border_colour
        self._label_colour = label_colour if label_colour is not None else COLOURS["white"]

        # Build the displayio sub-tree.
        self._group = displayio.Group()

        self._bg = RoundRect(
            x, y, width, height, CARD_RADIUS,
            fill=self._resting_fill,
            outline=border_colour,
            stroke=CARD_BORDER_WIDTH,
        )
        self._group.append(self._bg)

        # Icon, centred horizontally; positioned in the upper portion of the card.
        try:
            bitmap = displayio.OnDiskBitmap(icon_path)
            tile = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
            tile.x = x + (width - bitmap.width) // 2
            tile.y = y + (height - bitmap.height) // 2 - 14   # nudge up to leave label space
            self._group.append(tile)
        except OSError:
            # Missing BMP — proceed with text-only card. Useful before assets ship.
            pass

        # Label, centred horizontally, near the bottom of the card.
        # `label` may be a str (single line) or a sequence of strs (stacked
        # lines). When stacked, the block is centred on `label_y` and each
        # line is centred horizontally within the card.
        label_y = y + height - 22
        lines = list(label) if isinstance(label, (list, tuple)) else [label]
        line_stride = layout.CHAR_BASE_HEIGHT * label_scale + 2
        first_line_y = label_y - (len(lines) - 1) * line_stride // 2
        for i, line in enumerate(lines):
            line_y = first_line_y + i * line_stride
            self._group.append(
                layout.make_text_label(
                    text=line, scale=label_scale, color=self._label_colour,
                    x=x + width // 2 - layout.get_text_width(line, label_scale) // 2,
                    y=line_y,
                )
            )

        group.append(self._group)

    # ---------- Touch ----------

    def is_pressed(self, touch):
        """Hit-test against this card.

        ``touch`` must be already normalized — i.e. a (tx, ty) tuple in display
        coordinates, as returned by ``utils.touch.TouchTracker.poll()`` or
        ``utils.touch.normalize()``. Raw CST8xx coordinates are not accepted.
        """
        if self._hidden:
            return False
        tx, ty = touch[0], touch[1]
        return (self._x <= tx < self._x + self._w
                and self._y <= ty < self._y + self._h)

    def fire(self):
        if self._hidden:
            return
        import time as _t
        now = _t.monotonic()
        if now < self._next_fire_at:
            return  # tap debounce — suppress rapid repeat fires
        self._next_fire_at = now + TIMING["tap_debounce"]
        self._callback()

    # ---------- Visual feedback ----------

    def flash(self, now, duration=DEFAULT_FLASH_DURATION):
        """Set a non-blocking press feedback timer. Cleared by tick(now)."""
        self._flash_until = now + duration
        self._bg.fill = self._flash_fill

    def tick(self, now):
        if self._flash_until and now >= self._flash_until:
            self._bg.fill = self._resting_fill
            self._flash_until = 0.0

    # ---------- Visibility ----------

    def hide(self):
        self._hidden = True
        self._group.hidden = True

    def show(self):
        self._hidden = False
        self._group.hidden = False
