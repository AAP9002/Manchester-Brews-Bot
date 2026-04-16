import wifi
import displayio
import terminalio
from adafruit_display_text import label

class WifiIndicator:
    def __init__(self, x, y, display_group):
        self.group = displayio.Group()
        self.group.x = x
        self.group.y = y


        # Single bitmap with per-bar palette indices for strength display
        bar_width = 4
        bar_gap = 2
        bar_heights = [4, 8, 12, 16]
        self.num_bars = len(bar_heights)
        max_height = max(bar_heights)
        total_width = self.num_bars * bar_width + (self.num_bars - 1) * bar_gap
        bars_x_offset = 30

        # Palette: 0=transparent, 1-4=bar fill pixels, 5-8=bar border pixels
        self.palette = displayio.Palette(2 * self.num_bars + 1)
        self.palette[0] = 0x000000
        self.palette.make_transparent(0)
        for i in range(1, 2 * self.num_bars + 1):
            self.palette[i] = 0x333333

        self.bitmap = displayio.Bitmap(total_width, max_height, 2 * self.num_bars + 1)

        # Draw each bar: border pixels use index i+1+num_bars, fill pixels use index i+1
        x_pos = 0
        for i, h in enumerate(bar_heights):
            fill_idx = i + 1
            border_idx = i + 1 + self.num_bars
            for bx in range(bar_width):
                for by in range(h):
                    is_border = (bx == 0 or bx == bar_width - 1 or by == 0 or by == h - 1)
                    self.bitmap[x_pos + bx, max_height - 1 - by] = border_idx if is_border else fill_idx
            x_pos += bar_width + bar_gap

        self.tilegrid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette, x=bars_x_offset, y=0)
        self.group.append(self.tilegrid)

        display_group.append(self.group)

        # "No WiFi" overlay label — added to parent group so it sits over the status area
        self.no_wifi_label = label.Label(terminalio.FONT, text="No WiFi connection! :( ", color=0xFF0000, background_color=0x000000)
        self.no_wifi_label.x = 5
        self.no_wifi_label.y = 225
        self.no_wifi_label.scale = 2
        self.no_wifi_label.hidden = True
        display_group.append(self.no_wifi_label)

        self.update()

    def _rssi_to_level(self, rssi):
        if rssi > -50:
            return 4
        elif rssi > -60:
            return 3
        elif rssi > -70:
            return 2
        elif rssi > -80:
            return 1
        return 0

    def update(self):
        ap_info = wifi.radio.ap_info
        if ap_info is not None:
            rssi = ap_info.rssi
            level = self._rssi_to_level(rssi)
            print("WiFi RSSI: " + str(rssi) + " dBm (level " + str(level) + "/4)")
            # Color active bars based on strength
            if level >= 3:
                active_color = 0x00FF00  # green
            elif level == 2:
                active_color = 0xFFFF00  # yellow
            else:
                active_color = 0xFF8800  # orange
            for i in range(self.num_bars):
                color = active_color if i < level else 0x333333
                self.palette[i + 1] = color
                self.palette[i + 1 + self.num_bars] = color
            self.no_wifi_label.hidden = True
        else:
            print("WiFi: disconnected")
            for i in range(self.num_bars):
                self.palette[i + 1] = 0x000000
                self.palette[i + 1 + self.num_bars] = 0xFF0000
            self.no_wifi_label.hidden = False
