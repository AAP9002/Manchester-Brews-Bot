# v1 Baseline Notes

Captured at the start of the v2 refactor — symptoms of the v1 build that are NOT regressions of v2 work.

## 2026-05-06 — v1 freeze after first button press

**Observed on `main` (commit 9dc9d54), deployed to the Waveshare ESP32-S3.**

- Boot succeeds; `MenuScreen` renders; WiFi indicator turns on.
- Touch input registers and outbound HTTP requests are sent.
- After the request, the device stops responding — UI frozen.
- WiFi-indicator liveness was not observed at freeze time, so it is unknown whether the main loop is blocked or only the screen handler hung.

**Implication for v2:** if the freeze sits inside `SendRequest`/networking, it survives the refactor (P1.6 keeps that class). If it sits inside a v1 screen handler, P5.1 deletes it for free. Watch for the symptom returning after v2 screens are wired up in P4.5 — that would confirm a SendRequest/networking root cause and is the point to debug.

**Decision:** note-and-proceed. Not blocking pre-flight.
