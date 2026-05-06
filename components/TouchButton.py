import time
import displayio

from utils.config import TIMING


class TouchButton:
    # callback must be a callable, not the result of a call. Wrap with `lambda: ...`
    # at the call site if you need to pass arguments.
    def __init__(self, x, y, image_path, display_group, callback=None, padding=10,
                 transparent_color=None):
        self.image = displayio.OnDiskBitmap(image_path)
        self.x = x
        self.y = y
        self.callback = callback
        self.padding = padding
        self.hidden = False
        self._next_fire_at = 0.0

        # Safe width/height fallback (in case BMP metadata failed)
        self.width = getattr(self.image, "width", 200)
        self.height = getattr(self.image, "height", 200)

        if transparent_color is not None:
            try:
                self.image.pixel_shader.make_transparent(transparent_color)
            except (AttributeError, TypeError):
                pass

        self.tilegrid = displayio.TileGrid(
            self.image,
            pixel_shader=self.image.pixel_shader,
            x=self.x,
            y=self.y
        )

        display_group.append(self.tilegrid)

    def hideButton(self):
        self.tilegrid.hidden = True
        self.hidden = True

    def isPressed(self, touch):
        """Hit-test against this button.

        ``touch`` must be already normalized — i.e. a (tx, ty) tuple in display
        coordinates, as returned by ``utils.touch.TouchTracker.poll()`` or
        ``utils.touch.normalize()``. Raw CST8xx coordinates are not accepted.
        """
        if self.hidden:
            return False
        tx, ty = touch[0], touch[1]

        left   = self.x - self.padding
        right  = self.x + self.width + self.padding
        top    = self.y - self.padding
        bottom = self.y + self.height + self.padding

        return left <= tx <= right and top <= ty <= bottom

    def runCallback(self):
        if self.hidden:
            return
        now = time.monotonic()
        if now < self._next_fire_at:
            return
        self._next_fire_at = now + TIMING["tap_debounce"]
        if self.callback:
            self.callback()
