# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CircuitPython 9.2.8 firmware for a **Waveshare ESP32-S3 Touch LCD 2** (320x240 capacitive touch). It's a Slack-connected coffee gadget for the "Manchester-Brews" channel: announce brews (Brewing / Ready), flag low beans, and log brew counts to a Google Sheet.

There is no build step, no test suite, and no linter. Code runs on-device under CircuitPython.

**The architectural reference is [`V2-ARCHITECTURE.md`](V2-ARCHITECTURE.md).** This file is a short orientation; that file is the long-form spec for modules, navigation flows, touch model, and decisions.

## Deploying / running

The board mounts as a USB drive named `CIRCUITPY`. To deploy, copy the project files to that drive — `code.py` runs automatically on boot/save.

- `code.py` is the entry point (CircuitPython runs it on boot).
- `settings.toml` holds env vars read via `os.getenv(...)` (WiFi creds, the single Slack webhook, Google Sheet URL, `LOW_BEANS_PERSON`). It is `.gitignore`d; `settings.example.toml` is the template.
- `lib/` contains the bundled Adafruit `.mpy` modules — these must be deployed alongside the source.
- `deploy.sh` is a one-shot rsync that mirrors the working tree to the mounted `CIRCUITPY` volume; run it manually to deploy.
- `boot_out.txt` is written by CircuitPython on boot; do not edit.
- `sd/` is the SD card mount point; only `placeholder.txt` lives in the repo.

To iterate: edit a file, run `deploy.sh` to push to the board; CircuitPython auto-resets and reruns `code.py` once the copy lands. Use the serial console (e.g. `screen /dev/tty.usbmodem*` or Mu/Thonny) to see `print()` output and tracebacks.

## Architecture (short version)

Modules at a glance — see `V2-ARCHITECTURE.md` for the full picture.

- `code.py` — bootstrap + main loop only: WiFi connect, build display + touch, construct utilities, register screens, poll touches, tick the active screen, monitor WiFi.
- `utils/Navigator.py` — screen registry. `register(name, screen)`, `navigate(name, params)`, `active`. Owns the "current screen" concept; replaces the old string-keyed if-chains.
- `utils/touch.py` — single source of truth for touch. `normalize(raw)` does the 90° rotation; `TouchTracker.poll()` is edge-triggered (one event per physical press).
- `utils/config.py` — constants only: `DISPLAY`, `COLOURS`, `TIMING`, `MESSAGES`, `IMAGES`. No behaviour.
- `utils/layout.py` — text + position primitives (`make_text_label`, `get_text_width`, `truncate_to_width`, `split_title_lines`, `"center"` sentinel handling).
- `utils/SendRequest.py` — single device-wide `adafruit_requests.Session`, injected via constructor. Methods return `(ok, body)` so callers can distinguish offline from failed.
- `utils/CoffeeCounter.py` — Google Sheet brew log. Takes `SendRequest` + `AppState` via constructor.
- `utils/slack.py` — dispatches per-action message templates to the single `SEND_MESSAGE_SLACK_WEBHOOK`.
- `components/CardButton.py` — primary v2 button: rounded card, optional fill, BMP icon, label, non-blocking flash feedback.
- `components/TouchButton.py` — small BMP-only button (used for the back button on the announcement screen).
- `components/WifiIndicator.py` — kept but currently dormant on v2 screens (placement deferred).
- `screens/HomeScreen.py` — three `CardButton`s: Send announcement, Low on beans, Log your intake.
- `screens/AnnouncementScreen.py` — Brewing / Ready cards plus a small back button.
- `screens/SuccessScreen.py` — reusable confirmation screen; `on_enter(params)` accepts `message`, `image_path`, `return_to`, `duration`; `tick(now)` dismisses on timer.
- `screens/NoConnectionScreen.py` — full-screen offline state with reconnect polling; auto-navigates home when WiFi recovers.

## Things to know before editing

- **All hit-tests go through `utils.touch.normalize`.** Never inline the `tx = raw_y; ty = 240 - raw_x` rotation — that duplication is exactly what v2 deleted.
- **Touch dispatch is edge-triggered via `utils.touch.TouchTracker`.** Call `tracker.poll()` once per loop iteration; do not poll `ctp.touches` (or `ctp.touched`) directly in screens or components.
- **Visual feedback is non-blocking.** `card.flash(now)` records a timestamp; `card.tick(now)` clears it when the window expires. **No `time.sleep` for UI feedback** — v1's blocking sleeps froze the UI and dropped touches.
- **HTTP goes through one injected `SendRequest` instance.** Reuse the instance passed in via constructor; do not build another `Session`. Methods return `(ok, body)`; check `ok` before reading `body`.
- **Screens implement the Navigator protocol.** Each screen exposes `get_group()`, `on_enter(params)`, `handle_touch(touch)`, and `tick(now)`. Screens hold a navigator reference and call `self.navigator.navigate("home")` themselves — `code.py` does not branch on screen names.
- **Tap debounce is enforced at the button level.** Both `CardButton.fire` and `TouchButton.fire` gate on `TIMING["tap_debounce"]` (300 ms). Belt-and-braces on top of edge-triggered detection.
- **Settings are gitignored.** `settings.toml` carries live secrets and is excluded from git; `settings.example.toml` is the committed template. Never stage `settings.toml` or `boot_out.txt`. Name files explicitly when staging — no `git add -A`.
- **CircuitPython, not CPython.** No `asyncio` assumptions, no `typing` annotations on-device, prefer string concatenation over f-strings in tight memory paths (the codebase mixes both — match the surrounding style). Imports like `wifi`, `board`, `displayio`, `terminalio`, `microcontroller` only resolve on-device.

## Known gaps / deferred features

These are intentionally not yet built; see `V2-ARCHITECTURE.md` §11 "Deferred" for the full list.

- **`WifiIndicator` placement** — the component exists but is not wired into v2 screens; connectivity is communicated via `NoConnectionScreen` instead.
- **Stats screen** — `Coffee → MCR → Stats` flow is on the roadmap but not built.
- **Milestone messages** for "Log your intake" (e.g. nth-cup callouts).
- **React / emoji flow** — removed in v2; can return as a future feature.

## Git workflow

See [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) for the full rules. Summary:

- **One sub-task per branch**, cut from an up-to-date `main`. Naming: `type/short-kebab-description` (e.g. `feat/home-screen`, `fix/touch-debounce`).
- **Small atomic commits**, Conventional Commits format: `type(scope): imperative subject`. Body only when the *why* is non-obvious.
- Never stage `settings.toml` or `boot_out.txt`. Name files explicitly — no `git add -A`.
- Confirm with the user before `git push`, `git merge`, opening a PR, force-pushing, or rewriting shared history.
