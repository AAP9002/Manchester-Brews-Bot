# Open questions — resolved

All four questions have been answered. Each section below records the decision so the implementing agent has the answer in context.

---

## Q1 — New card-icon BMPs

**Status:** RESOLVED — text-only fallback for now

The icons (`announcement.bmp`, `low-beans.bmp`, `log-intake.bmp`) are not yet exported. P4.2 ships text-only cards by relying on `CardButton`'s missing-BMP fallback (the constructor catches `OSError` and proceeds without the icon).

**Action when assets land:** drop the BMPs into `/images/` matching the paths in `utils/config.py:IMAGES`. No code change required.

---

## Q2 — "Alex" name in the Low-on-beans message

**Status:** RESOLVED — configurable via `LOW_BEANS_PERSON` env var

`MESSAGES["low_on_beans"]` in `utils/config.py` carries a `{name}` placeholder. `HomeScreen._fire_low_beans` reads `os.getenv("LOW_BEANS_PERSON")` (default `"Someone"`) and `.format(name=...)`s the subtitle line at runtime.

**Already wired into:**
- `tasks/v2/P1.4-config-module.md` — template form documented
- `tasks/v2/P1.2-settings-example.md` — `LOW_BEANS_PERSON` line added
- `tasks/v2/P4.2-homescreen.md` — formatting code shown

---

## Q3 — Back-button debounce on AnnouncementScreen

**Status:** RESOLVED — 300 ms debounce applied at the button level

Both `TouchButton.fire` (P1.5) and `CardButton.fire` (P2.1) gate their callback by `TIMING["tap_debounce"]` (300 ms). A button cannot fire twice within that window.

This is layered on top of the edge-triggered `TouchTracker` — the tracker prevents the same physical press from firing repeatedly; the debounce protects against deliberately-rapid sequential presses (especially the back button).

**Already wired into:**
- `tasks/v2/P1.5-touchbutton-refactor.md` — debounce snippet specified
- `tasks/v2/P2.1-cardbutton.md` — `_next_fire_at` initialised; `fire()` gated

---

## Q4 — WifiIndicator placement on v2 screens

**Status:** RESOLVED — deferred

v2 communicates connectivity state via the dedicated `NoConnectionScreen` (P4.4) which auto-navigates back to `home` on reconnect. The standalone `WifiIndicator` stays dormant — code is preserved but is not mounted on any v2 screen.

**Action when revisited:** decide on placement (likely a small chip in a top-right corner across all screens, or a future top status bar) and add a follow-up task to mount it.
