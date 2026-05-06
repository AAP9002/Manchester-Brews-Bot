import displayio

class TouchButton:
    def __init__(self, x, y, image_path, display_group, callback=None, padding=10):
        self.image = displayio.OnDiskBitmap(image_path)
        self.x = x
        self.y = y
        self.callback = callback
        self.padding = padding
        self.hidden = False

        # Safe width/height fallback (in case BMP metadata failed)
        self.width = getattr(self.image, "width", 200)
        self.height = getattr(self.image, "height", 200)

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
        if self.hidden:
            return False
        raw_x, raw_y = touch["x"], touch["y"]

        tx = raw_y
        ty = 240 - raw_x

        left   = self.x - self.padding
        right  = self.x + self.width + self.padding
        top    = self.y - self.padding
        bottom = self.y + self.height + self.padding

        return left <= tx <= right and top <= ty <= bottom

    def runCallback(self):
        if self.hidden:
            return
        if self.callback:
            self.callback()