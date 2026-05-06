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

Two single-source-of-truth responsibilities:

1. **Coordinate normalization** — convert raw CST8xx touches to display coordinates.
   ```
   def normalize(raw_touch):  # (x, y, ...) → (tx, ty) with 90° rotation applied
   ```

2. **Edge-triggered touch detection** — a single physical press fires the callback once, not every loop iteration the finger is held down.
   ```
   class TouchTracker:
       def __init__(self, ctp): ...
       def poll(self) -> Optional[tuple]:
           """Return the normalized touch on the rising edge of a press, else None."""
   ```

The main loop calls `tracker.poll()` once per iteration and forwards any returned touch to `navigator.active.handle_touch(...)`. Used by `CardButton.is_pressed`, `TouchButton.is_pressed`, and any future hit-tests.

### `utils/config.py` (new)

Constants only — no behaviour:

```
DISPLAY  = { "width": 320, "height": 240 }
COLOURS  = { "blue": 0x2563EB, "red": 0xEF4444, "teal": 0x14B8A6,
             "success": 0x16A34A, "dark": 0x111827, "white": 0xFFFFFF }
TIMING   = { "success_dismiss": 2.5, "wifi_poll": 5.0, "tap_debounce": 0.3 }
MESSAGES = {
    # The {name} placeholder is filled at runtime from env var LOW_BEANS_PERSON
    # (default "Someone" if unset).
    "low_on_beans": ("{name} has been peer-pressured effectively...",
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

### `utils/layout.py` (new)

Text and layout primitives used by every screen. No state, no I/O. Patterns ported (with light cleanup) from a sister CircuitPython codebase that proved them out:

- `CHAR_BASE_WIDTH = 5`, `CHAR_BASE_HEIGHT = 8`, `CHAR_BASE_GAP = 1` (terminalio.FONT metrics)
- `get_text_width(text, scale)` — width in pixels using the font metrics above
- `make_text_label(text, scale, color, x, y)` — wrap `label.Label` with the project's anchoring rules; supports `"center"` as a sentinel for the x or y argument
- `resolve_text_position(value, parent_size, offset)` — handle the `"center"` sentinel
- `truncate_to_width(text, scale, max_width)` — ellipsis truncation if too long
- `split_title_lines(text, scale, max_width)` — wrap into up to N lines; final line gets ellipsis truncation if needed

Replaces the hand-coded position arithmetic strewn through v1 (`x=25, y=85` magic numbers).

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
    .fire()                          # callback always callable; never invoked at construction
    .flash(now)                      # set non-blocking press feedback timer
    .tick(now)                       # called by parent screen; clears flash when expired
```

Renders: optional fill `RoundRect`, border `RoundRect` in `border_colour`, centred BMP icon, label text underneath using `utils/layout` primitives. Hit-test uses the full card bounds.

Visual press feedback uses a timestamp model — `flash(now)` sets `_flash_until = now + 0.18`; the parent screen's `tick(now)` calls `card.tick(now)` which restores the resting fill once `now >= _flash_until`. **No `time.sleep` for feedback** (v1 used 2-second blocking sleeps which froze the UI and dropped touch input).

**Tap debounce.** `fire()` gates its callback by `TIMING["tap_debounce"]` (300 ms) — a button cannot fire twice within that window. Edge-triggered touch already prevents the same physical press from firing twice; this protects against deliberately-rapid sequential presses (especially the back button).

### `components/TouchButton.py` (keep, light refactor)

- Drop the duplicated rotation logic; call `touch.normalize`
- Constructor accepts `callback` only as a callable; rely on lambdas at call sites
- `fire()` gates the callback by `TIMING["tap_debounce"]` (same as CardButton)
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
ctp.touched (every loop iter)
        │
        ▼
TouchTracker.poll()        ← rising-edge: returns a touch only on the
        │                    transition from "not touching" to "touching"
        ▼
utils/touch.normalize() → (tx, ty)
        │
        ▼
navigator.active.handle_touch((tx, ty))
        │
        ▼
component.is_pressed(raw)   ← every component normalizes once
        │
        ▼
component.fire() → callback (always callable; never invoked at construction)
        │
        ▼
component.flash(now)        ← non-blocking press feedback; cleared on tick
```

Edge-triggered detection prevents a single physical press from firing the same callback dozens of times during a frame. v1's continuous-poll model made that a real risk, masked only by the blocking sleeps inside screen handlers — which v2 removes.

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
- Webhook list shrinks from 7 to 1 (`SEND_MESSAGE_SLACK_WEBHOOK`); per-action message content is templated in `utils/config.SLACK_MESSAGES` and dispatched via `utils/slack.py`
- `UPDATE_INTERVAL_MS` removed (was already dead config in v1; `WEATHER_LAT` / `WEATHER_LON` removed alongside the weather feature)

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
  layout.py
  touch.py
  config.py

images/                              (existing + new card icons)
lib/                                 (Adafruit, unchanged)
sd/                                  (unchanged)
```

**Deleted**: `screens/MenuScreen.py`, `screens/BroadcastScreen.py`, `screens/ReactScreen.py`, `images/react*.bmp`, react-emoji BMPs. (`utils/WeatherManager.py` and weather state already removed in batch B.)

---

## 11. Implementation phases

Phases are ordered so the device boots into a working state at the end of each. Phase 4 is the only flag-day swap.

### Phase 1 — Foundation (no behaviour change)
1. Create `.gitignore` (exclude `settings.toml`, `__pycache__`, `boot_out.txt`)
2. Create `settings.example.toml` with placeholder values
3. Create `utils/touch.py` with `normalize()` and `TouchTracker`
4. Create `utils/config.py` (colours, timing, messages, image paths)
5. Create `utils/layout.py` (text + layout primitives)
6. Refactor `components/TouchButton.py` to call `touch.normalize`
7. Refactor `utils/SendRequest.py` to take `AppState` via constructor; return `(ok, body)`
8. Update `code.py` and existing screens to construct `SendRequest` instance and adapt to the new return shape
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
17. ~~Delete `utils/WeatherManager.py` and weather state~~ — done in batch B
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

## 12. Resolved decisions

- **Card-icon BMPs (Q1):** not yet exported. P4.2 ships text-only cards via `CardButton`'s missing-BMP fallback; BMPs drop in later as a no-code change.
- **Low-on-beans person name (Q2):** **configurable** via `LOW_BEANS_PERSON` env var in `settings.toml`. `MESSAGES["low_on_beans"]` carries a `{name}` placeholder; `HomeScreen` formats it at runtime, defaulting to `"Someone"` if the env var is unset.
- **Tap debounce (Q3):** **300 ms debounce applied at the button level** for both `TouchButton.fire` and `CardButton.fire` via `TIMING["tap_debounce"]`. Belt-and-braces protection on top of edge-triggered detection.
- **WifiIndicator placement (Q4):** **deferred.** v2 communicates connectivity via `NoConnectionScreen`; the standalone indicator stays dormant until a future pass.

---

## 13. Borrowed patterns (provenance)

`utils/layout.py`, `TouchTracker`, and the non-blocking flash model in `CardButton` were lifted (with modifications) from a sister CircuitPython codebase that targets the same hardware family. Borrowed for code-quality reasons only — none of the borrowed code carries new functionality. **Not borrowed**: idle/sleep mode, top-of-screen status bar with clock, NTP sync, JSON state persistence — all out of scope for v2.
