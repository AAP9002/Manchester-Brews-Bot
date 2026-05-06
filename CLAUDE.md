# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CircuitPython 9.2.8 firmware for a **Waveshare ESP32-S3 Touch LCD 2** (320x240 capacitive touch). It's a Slack-connected coffee gadget for the "Manchester-Brews" channel: announce brews, send emoji reactions, log brew counts to a Google Sheet, and show local weather.

There is no build step, no test suite, and no linter. Code runs on-device under CircuitPython.

## Deploying / running

The board mounts as a USB drive named `CIRCUITPY`. To deploy, copy the project files to that drive — `code.py` runs automatically on boot/save.

- `code.py` is the entry point (CircuitPython runs it on boot).
- `settings.toml` holds env vars read via `os.getenv(...)` (WiFi creds, Slack webhooks, Google Sheet URL, weather lat/lon). The board re-reads it on reset.
- `lib/` contains the bundled Adafruit `.mpy` modules — these must be deployed alongside the source.
- `boot_out.txt` is written by CircuitPython on boot; do not edit.
- `sd/` is the SD card mount point; only `placeholder.txt` lives in the repo.

To iterate: edit a file, save, the board auto-resets and reruns `code.py`. Use the serial console (e.g. `screen /dev/tty.usbmodem*` or Mu/Thonny) to see `print()` output and tracebacks.

## Architecture

### Shared mutable state

`code.py` constructs one `app_state` dict and threads it everywhere. Three utility classes (`SendRequest`, `CoffeeCounter`, `WeatherManager`) hold it on a **class attribute** rather than receiving it through method args:

```python
SendRequest.app_state = app_state
CoffeeCounter.app_state = app_state
WeatherManager.app_state = app_state
```

Treat these as singletons — there is one shared state and one HTTP session for the whole device. Don't instantiate them.

`app_state` keys: `current_screen`, `last_brew_time`, `reset_react_options`, `wifi_connected`, `coffee_count`, `weather_temp`, `weather_condition`, `weather_rain_chance`.

### Screens and the main loop

Each screen (`MenuScreen`, `BroadcastScreen`, `ReactScreen`) builds its `displayio.Group` once in `__init__` via `build()` and exposes `get_screen()`, `is_button_pressed(touch)`, `fire_button_callback(touch)`. `code.py` instantiates all screens up front and swaps the active one by reassigning `display.root_group` whenever `app_state["current_screen"]` changes.

The main loop polls `ctp.touches` continuously and dispatches based on `current_screen`. It also runs a 5-second cadence that updates the WiFi indicator, attempts auto-reconnect on drop, and refreshes weather every 10 minutes.

To add a screen: build it in `code.py`, give it a string name in `app_state["current_screen"]`, add a dispatch branch in the touch loop, and add a branch in the screen-switching block that sets `display.root_group`.

### Touch coordinate rotation

The CST8xx driver returns raw touch coords that are rotated 90° relative to the display. Every hit-test in this codebase converts via:

```python
tx = raw_y
ty = 240 - raw_x
```

`TouchButton.isPressed` does this internally. If you write a new hit-test (see `MenuScreen.isPlusOnePressed` / `isLowBeansPressed`), you must apply the same rotation — bitmap coordinates and touch coordinates do **not** share an axis.

### Networking

All HTTP goes through `utils/SendRequest.py`, which owns a single `adafruit_requests.Session` built from a shared socket pool. Every request closes connections and runs `gc.collect()` in a `finally` — memory is tight on the ESP32-S3 and leaked sockets cause subsequent requests to fail. Reuse `SendRequest.post/get`; do not create another session.

`SendRequest` short-circuits to `None` when `app_state["wifi_connected"]` is False, so callers can call it unconditionally.

### External integrations

- **Slack**: each action posts to a separate Slack Workflow webhook URL. Webhook URLs live in `settings.toml`; the receiving workflow expects `{"messageContent": "..."}`. Adding a new emoji reaction = new webhook + new entry in `settings.toml` + new `os.getenv` read.
- **Google Apps Script** (`google-apps-script.js`): the coffee log backend. `GET ?action=log` appends a timestamped row and returns `{count}`; bare `GET` returns `{count}`. Deploy instructions are in the file header. The deployed Web App URL goes into `settings.toml` as `GOOGLE_SHEET_URL`.
- **Open-Meteo** (`utils/WeatherManager.py`): no API key; uses `WEATHER_LAT`/`WEATHER_LON` from settings. WMO weather codes are mapped to short condition strings in `_WMO_CONDITIONS`.

### Bruno collection

`bruno/BREWS-CHANNEL/` is a [Bruno](https://www.usebruno.com/) API client collection for exercising the Slack webhooks without flashing the device.

## Things to know before editing

- **`ReactScreen` is currently disabled** — imports, instantiation, and dispatch are commented out in `code.py`. It also has a latent bug: `TouchButton(..., callback=SendRequest.post(WEBHOOK_URL))` *invokes* `post` at construction time instead of passing a callable, so re-enabling it as-is would fire every webhook on screen build. Fix by passing `lambda: SendRequest.post(WEBHOOK_URL)` (or equivalent) before re-enabling.
- **CircuitPython, not CPython.** No `asyncio` assumptions, no `typing` annotations on the device, prefer string concatenation over f-strings in tight memory paths (the codebase mixes both — match the surrounding style). Imports like `wifi`, `board`, `displayio`, `terminalio`, `microcontroller` only resolve on-device.
- **`settings.toml` contains live secrets** (WiFi password, Slack webhook URLs). The repo currently has no `.gitignore` and no commits — do not push without addressing this first.
