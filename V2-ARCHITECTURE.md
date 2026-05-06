# Coffee Bot v2 — Architecture HLD

CircuitPython firmware refactor for the Waveshare ESP32-S3 Touch LCD 2 coffee gadget. This document is the load-bearing reference for v2; `CLAUDE.md` will be updated to point here once Phase 5 lands.

---

## 1. Why v2

v1 works but has accumulated structural problems:

- **Dead code with live bugs.** `ReactScreen` is commented out and contains a callback-at-construction-time bug that also exists in `BroadcastScreen`.
- **Monolithic screens.** `MenuScreen` is 296 lines mixing layout, animation, touch dispatch, and HTTP.
- **Duplicated touch rotation.** `tx = raw_y; ty = 240 - raw_x` is copy-pasted in three places.
- **Hidden coupling.** State is threaded via `SendRequest.app_state = app_state` class-attribute assignment.
- **Magic numbers everywhere.** Colours, positions, debounce thresholds, RSSI cutoffs scattered across files.
- **No screen routing.** `code.py` has if-chains keyed on screen-name strings.

v2 is a structural rewrite paired with the new card-based visual design.

---

## 2. Goals & non-goals

**Goals**
- New card-based home screen and announcement screen matching the design files
- One reusable `SuccessScreen` for all action confirmations (Low on beans, Log intake, Brewing, Ready)
- Dedicated `NoConnectionScreen` with auto-recovery on reconnect
- One canonical place for: touch coordinate transforms, screen routing, configuration constants
- Eliminate the construction-time callback bug pattern
- Slim `code.py` to bootstrap + event loop only

**Non-goals (this pass)**
- Async / multitasking — CircuitPython is single-thread on this board, blocking I/O is acceptable
- Weather display (removed)
- Emoji react flow (removed; can return as a future feature)
- Stats screen (deferred)
- CPython-side test harness

---

## 3. System diagram

```
┌──────────────────────────────────────────────────────────────┐
│                          code.py                             │
│      bootstrap • main loop • touch poll • wifi check         │
└────────────┬─────────────────────────────────────────────────┘
             │ delegates to
             ▼
┌──────────────────────────────────────────────────────────────┐
│                     Navigator (utils)                        │
│   screen registry • active screen • navigate(name, params)   │
└─────┬─────────────┬──────────────┬───────────────┬───────────┘
      │             │              │               │
      ▼             ▼              ▼               ▼
┌──────────┐  ┌──────────────┐  ┌─────────┐  ┌────────────────┐
│ Home     │  │ Announcement │  │ Success │  │ NoConnection   │
│ Screen   │  │ Screen       │  │ Screen  │  │ Screen         │
└────┬─────┘  └──────┬───────┘  └─────────┘  └────────────────┘
     │               │
     │ uses          │ uses
     ▼               ▼
┌──────────────────────────────────────────────────────────────┐
│   CardButton • TouchButton • WifiIndicator (components)      │
│             every hit-test → utils/touch.normalize()         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  SendRequest → CoffeeCounter (utils)                         │
│  one device-wide HTTP session, injected via constructor      │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Modules

### `code.py` (target ~60 lines, down from 131)

1. WiFi connect → instantiate `AppState`
2. Build display + capacitive touch driver
3. Construct utilities (`SendRequest`, `CoffeeCounter`) with state injected
4. Construct each screen with the navigator + needed utilities passed in
5. Register screens with navigator, navigate to `home`
6. Main loop: poll touches → forward to `navigator.active`, check WiFi every 5 s, run `navigator.active.tick(now)` for time-based behaviours

### `utils/Navigator.py` (new)

```
class Navigator:
    register(name, screen)
    navigate(name, params=None)   # swaps display.root_group; calls screen.on_enter(params)
    active                        # current screen instance
    active_name                   # current screen name
```

Replaces the `if app_state["current_screen"] == "..."` chains. Screens hold a navigator reference and call `navigator.navigate("home")` themselves.

### `utils/touch.py` (new)

```
def normalize(raw_touch):  # (x, y) → (tx, ty) with 90° rotation applied
```

The single place this transform lives. Used by `CardButton.is_pressed`, `TouchButton.is_pressed`, and any future hit-tests.

### `utils/config.py` (new)

Constants only — no behaviour:

```
DISPLAY  = { "width": 320, "height": 240 }
COLOURS  = { "blue": 0x2563EB, "red": 0xEF4444, "teal": 0x14B8A6,
             "success": 0x16A34A, "dark": 0x111827, "white": 0xFFFFFF }
TIMING   = { "success_dismiss": 2.5, "wifi_poll": 5.0, "tap_debounce": 0.3 }
MESSAGES = {
    "low_on_beans": ("Alex has been peer-pressured effectively...",
                     "beans should be with you shortly"),
    "log_intake_default": "Cup logged.",
    "brewing": "Brewing announced",
    "ready":   "Ready announced",
    "no_connection": "No internet connection",
}
IMAGES   = {
    "send_icon":       "/images/announcement.bmp",
    "low_beans_icon":  "/images/low-beans.bmp",
    "log_intake_icon": "/images/log-intake.bmp",
    "brewing_icon":    "/images/loading.bmp",
    "ready_icon":      "/images/coffee-done.bmp",
    "back_icon":       "/images/back.bmp",
}
```

### `utils/SendRequest.py` (refactor)

- Constructor takes `AppState` (DI, not class-attribute assignment)
- Same single-session pattern, same `_cleanup` finally block
- Methods return `(ok: bool, body: dict | None)` so callers can distinguish "offline" from "request failed"

### `utils/CoffeeCounter.py` (light refactor)

- Constructor takes `SendRequest` instance + `AppState`
- Same semantics; remove redundant `app_state is None` guards

### `components/CardButton.py` (new)

Primary button type for the v2 designs.

```
CardButton(group, x, y, width, height,
           icon_path, label, border_colour,
           callback, fill_colour=None)
    .is_pressed(raw_touch) -> bool   # uses utils/touch.normalize
    .fire()                          # callback always a callable; never invoked at construction
```

Renders: optional fill `RoundRect`, border `RoundRect` in `border_colour`, centred BMP icon, label text underneath. Hit-test uses the full card bounds.

### `components/TouchButton.py` (keep, light refactor)

- Drop the duplicated rotation logic; call `touch.normalize`
- Constructor accepts `callback` only as a callable; rely on lambdas at call sites
- Used for the back button on `AnnouncementScreen` and any future BMP-only buttons

### `components/WifiIndicator.py` (keep, defer)

Placement on v2 screens to be specified later. Code unchanged in this pass; not wired into the v2 home screen.

### `screens/HomeScreen.py` (new, replaces `MenuScreen`)

Three `CardButton` instances per the design:

| Card | Action |
|---|---|
| **Send announcement** (left half, blue fill) | `navigator.navigate("announcement")` |
| **Low on beans** (top right, red border) | POST low-beans webhook → `navigate("success", {message: MESSAGES["low_on_beans"], return_to: "home"})` |
| **Log your intake** (bottom right, teal border) | `counter.increment(); counter.sync()` → `navigate("success", {message: MESSAGES["log_intake_default"], return_to: "home"})` |

### `screens/AnnouncementScreen.py` (new, replaces `BroadcastScreen`)

Two `CardButton` instances + small back `TouchButton` bottom-right:

| Element | Action |
|---|---|
| **Brewing** | POST brewing webhook → `success({image: IMAGES["brewing_icon"], return_to: "home"})` |
| **Ready** | POST ready webhook → `success({image: IMAGES["ready_icon"], return_to: "home"})` |
| **Back** | `navigator.navigate("home")` |

### `screens/SuccessScreen.py` (new, reusable)

```
on_enter(params):
    params = {
        "message":    str | (subtitle, main),    # str = single centred line; tuple = two lines
        "image_path": Optional[str],             # if present, replaces the checkmark
        "return_to":  str,                       # screen name to navigate back to
        "duration":   float,                     # seconds; defaults to TIMING["success_dismiss"]
    }
    rebuild display group: green background, message, image-or-checkmark
    self._dismiss_at = monotonic() + duration

tick(now):
    if now >= self._dismiss_at:
        navigator.navigate(self._return_to)
```

### `screens/NoConnectionScreen.py` (new)

- Static layout: full-screen warning, message from `MESSAGES["no_connection"]`
- `tick(now)` polls `state.wifi_connected`; navigates to `home` when reconnected
- Owns the reconnect attempt itself (calls `wifi.radio.connect(...)` on a backoff)

---

## 5. State model

```python
class AppState:
    wifi_connected: bool
    coffee_count: int
    last_brew_time: float | None
```

Removed from v1: `weather_*`, `reset_react_options`, `current_screen` (Navigator owns that).

---

## 6. Navigation flows

```
home ─[Send announcement]─→ announcement ─[Brewing]─→ success ─→ home
                                          ─[Ready]──→ success ─→ home
                                          ─[Back]───→ home

home ─[Low on beans]──────→ success ─→ home
home ─[Log your intake]───→ success ─→ home

ANY  ─[wifi drop]─────────→ no_connection ─[wifi up]→ home
```

---

## 7. Touch input model

```
raw_touch from CST8xx
        │
        ▼
utils/touch.normalize() → (tx, ty)
        │
        ▼
component.is_pressed(raw)   ← every component normalizes once
        │
        ▼
component.fire() → callback (always callable; never invoked at construction)
```

---

## 8. Network & error handling

- All HTTP through one `SendRequest` instance with one `adafruit_requests.Session`
- Every request: `try/finally` → close → `gc.collect()` (unchanged from v1)
- Calls return `(ok: bool, body: dict | None)` so screens can branch on failure
- Failures during success-screen flows: still show success briefly (the action was attempted) — log to serial; don't crash. A future "failure" variant of `SuccessScreen` (red background) is a clean extension point.

---

## 9. Configuration & secrets

- `settings.toml` is now `.gitignore`d
- Add `settings.example.toml` with placeholder values
- Webhook list shrinks from 7 to 4: send-message, brewing, ready, low-beans (no react webhooks)
- `WEATHER_LAT` / `WEATHER_LON` / `UPDATE_INTERVAL_MS` removed

---

## 10. File structure (final)

```
code.py
.gitignore
settings.example.toml
settings.toml                       (gitignored)
V2-ARCHITECTURE.md
CLAUDE.md
deploy.sh
google-apps-script.js

screens/
  HomeScreen.py
  AnnouncementScreen.py
  SuccessScreen.py
  NoConnectionScreen.py

components/
  CardButton.py
  TouchButton.py
  WifiIndicator.py

utils/
  Navigator.py
  SendRequest.py
  CoffeeCounter.py
  touch.py
  config.py

images/                              (existing + new card icons)
lib/                                 (Adafruit, unchanged)
sd/                                  (unchanged)
```

**Deleted**: `screens/MenuScreen.py`, `screens/BroadcastScreen.py`, `screens/ReactScreen.py`, `utils/WeatherManager.py`, `images/react*.bmp`, react-emoji BMPs.

---

## 11. Implementation phases

Phases are ordered so the device boots into a working state at the end of each. Phase 4 is the only flag-day swap.

### Phase 1 — Foundation (no behaviour change)
1. Create `.gitignore` (exclude `settings.toml`, `__pycache__`, `boot_out.txt`)
2. Create `settings.example.toml` with placeholder values
3. Create `utils/touch.py` with `normalize()`
4. Create `utils/config.py` (colours, timing, messages, image paths)
5. Refactor `components/TouchButton.py` to call `touch.normalize`
6. Refactor `utils/SendRequest.py` to take `AppState` via constructor; return `(ok, body)`
7. Update `code.py` and existing screens to construct `SendRequest` instance and adapt to the new return shape
   - **Verify on-device: v1 still works end-to-end.**

### Phase 2 — Components
8. Build `components/CardButton.py` plus a smoke screen to render one
   - **Verify on-device: card renders, hit-test fires its callback exactly on press.**

### Phase 3 — Navigator
9. Build `utils/Navigator.py` (register, navigate, active, tick)
10. Migrate `code.py` main loop to use `Navigator` while still pointing at `MenuScreen` / `BroadcastScreen`
    - **Verify on-device: existing screens still work via Navigator.**

### Phase 4 — New screens (the design switchover)
11. Build `screens/SuccessScreen.py` (reusable, with `on_enter` / `tick`)
12. Build `screens/HomeScreen.py` (3 `CardButton`s)
13. Build `screens/AnnouncementScreen.py` (2 `CardButton`s + back)
14. Build `screens/NoConnectionScreen.py` (offline state + reconnect poll)
15. Wire all four screens into Navigator; switch boot to `home`
    - **Verify on-device: all flows work — including WiFi drop / recover.**

### Phase 5 — Cleanup
16. Delete `MenuScreen.py`, `BroadcastScreen.py`, `ReactScreen.py`
17. Delete `utils/WeatherManager.py` and weather state
18. Remove unused BMPs (`react*.bmp`, emoji react icons)
19. Trim react webhook entries from `settings.example.toml`
20. Update `CLAUDE.md` to describe v2 architecture (this doc becomes the reference)

### Deferred
- `WifiIndicator` placement on v2 screens
- Stats screen (`Coffee → MCR → Stats`)
- Milestone messages for "Log your intake"
- Brewing / Ready transition animations richer than the static `SuccessScreen`
- React / emoji flow

---

## 12. Open questions

- New card-icon BMPs are not yet in `/images` — exports needed for: bell-on-cup (Send announcement), low-beans, log-intake bar chart
- "Alex" in the Low-on-beans message — hard-code or expose as `LOW_BEANS_PERSON` env var in `settings.toml`?
- Does the back button on `AnnouncementScreen` need its own debounce, or is the existing `TouchButton` press model sufficient?
