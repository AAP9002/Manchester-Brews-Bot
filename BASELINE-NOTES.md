# v1 Baseline Notes

Captured at the start of the v2 refactor — symptoms of the v1 build that are NOT regressions of v2 work, plus prerequisite work that must happen before specific v2 phases.

## 2026-05-06 — v1 freeze after first button press

**Observed on `main` (commit 9dc9d54), deployed to the Waveshare ESP32-S3.**

- Boot succeeds; `MenuScreen` renders; WiFi indicator turns on.
- Touch input registers and outbound HTTP requests are sent.
- After the request, the device stops responding — UI frozen.
- WiFi-indicator liveness was not observed at freeze time, so it is unknown whether the main loop is blocked or only the screen handler hung.

**Implication for v2:** if the freeze sits inside `SendRequest`/networking, it survives the refactor (P1.6 keeps that class). If it sits inside a v1 screen handler, P5.1 deletes it for free. Watch for the symptom returning after v2 screens are wired up in P4.5 — that would confirm a SendRequest/networking root cause and is the point to debug.

**Decision:** note-and-proceed. Not blocking pre-flight.

## 2026-05-06 — Phase 4 prerequisite: three new Slack Workflow webhooks

v1 uses a single `SEND_MESSAGE_SLACK_WEBHOOK` for the "Brewing", "Ready", and "Low on beans" buttons. v2 splits these so each Slack Workflow can post different content. Before launching the Phase 4 agents (P4.2 / P4.3), the user must:

1. Create three new Slack Workflows in the Manchester-Brews workspace and copy their webhook URLs.
2. Add to `settings.toml`:
   - `LOW_ON_BEANS_WEBHOOK`
   - `BREWING_WEBHOOK`
   - `READY_WEBHOOK`
3. Confirm `LOW_BEANS_PERSON` is set per `tasks/v2/open-questions.md` Q2 (already resolved per the orchestrator).

Existing `SEND_MESSAGE_SLACK_WEBHOOK` and `GOOGLE_SHEET_URL` already match the v2 spec — no rename needed.

Not blocking Phases 1–3. Also: P1.2 will produce `settings.example.toml` documenting the canonical v2 schema, which will surface this again.

## Cleanup carried by P5.3

Items found during pre-flight that the existing Phase 5 cleanup task already covers — listed here so they aren't lost:

- `UPDATE_INTERVAL_MS = 2000` in `settings.toml` is unreferenced by any `getenv` call (dead config).
- Seven `*_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK` keys exist for the disabled `ReactScreen`; P5.1 deletes the screen, P5.3 deletes the webhook config.
