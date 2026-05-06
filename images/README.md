# Image assets

CircuitPython's `displayio.OnDiskBitmap` reads the BMPs in this folder. Paths and
filenames are declared in `utils/config.py` under `IMAGES`.

## Format

- **BMP only** (CircuitPython does not decode PNG/JPEG natively).
- 24-bit (opaque) is the safe default; existing `loading.bmp` and
  `coffee-done.bmp` are 24-bit.
- For transparency, either:
  - export as an **indexed (≤8-bit) BMP** with the background colour as palette
    entry 0, or
  - keep a solid background colour and let the loader call
    `pixel_shader.make_transparent(<rgb>)` (this is how the back button
    handles its black background — see `components/TouchButton.py`).
- Avoid anti-aliased edges if you plan to make a colour transparent — only
  exact-match pixels become transparent, so anti-alias halos will remain.

## Currently present

| File              | Size    | Bit depth | Used by                            |
| ----------------- | ------- | --------- | ---------------------------------- |
| `back.bmp`        | 45×45   | 32-bit    | `AnnouncementScreen` back button   |
| `loading.bmp`     | 124×124 | 24-bit    | `AnnouncementScreen` Brewing card  |
| `coffee-done.bmp` | 128×128 | 24-bit    | `AnnouncementScreen` Ready card    |

## Missing — please add

All three are used by `HomeScreen`. Card layout: 320×240 display, 8 px padding.

- Left "Send" card: 148 wide × 224 tall.
- Right cards (Low on beans, Log intake): 148 wide × 108 tall each.

The icon is centred horizontally and nudged up 14 px from card-centre to leave
room for the label at the bottom.

| File               | Recommended size | Card slot         | Used by                          |
| ------------------ | ---------------- | ----------------- | -------------------------------- |
| `announcement.bmp` | 120×120          | 148×224 left card | `HomeScreen` "Send announcement" |
| `low-beans.bmp`    | 64×64            | 148×108 right top | `HomeScreen` "Low on beans"      |
| `log-intake.bmp`   | 64×64            | 148×108 right bot | `HomeScreen` "Log your intake"   |

Sizes are recommendations — the cards will render whatever you provide as long
as it fits. For the tall left card, anything up to ~128×128 works; for the
short right cards, keep the icon ≤ ~78 px tall so it doesn't collide with the
label.
