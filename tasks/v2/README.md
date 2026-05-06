# Coffee Bot v2 — Task Index

Self-contained task files for the v2 refactor. Each `.md` here can be handed to an independent agent without conversation context — read the file, read the linked HLD sections, do the work, mark it done.

**Authoritative architecture reference:** `../../V2-ARCHITECTURE.md` (project root).

---

## How to use this directory

1. Pick a task whose `Depends on` list is satisfied (all listed tasks marked `done`).
2. Read the task file end-to-end — `Context`, `Files to touch`, `Specification`, `Acceptance criteria`, `Out of scope`.
3. Read the HLD sections it references.
4. Read the source files it lists.
5. Do the work. Stay inside the task's stated scope — do not refactor neighbouring code.
6. Update the `Status:` line at the top of the task file from `not-started` → `in-progress` → `done` as you go.
7. The user is responsible for on-device verification between agent runs; verification steps in each task tell them what to check.

If the task uncovers a problem that can't be solved without expanding scope, stop and write the issue under a `## Notes` section at the bottom of the task file rather than silently growing the change.

---

## Dependency graph

```
P1.1  ─┐
P1.2  ─┤
P1.3  ─┼── (parallel batch A — no dependencies)
P1.4  ─┤
P1.6  ─┘
        │
P1.5  ──┴─ depends on P1.3
P1.7  ──── depends on P1.6
        │
P2.1  ──── depends on P1.3, P1.4
P3.1  ──── depends on P1.3, P1.4
P3.2  ──── depends on P3.1, P1.7
        │
P4.1  ──── depends on P3.1, P1.4
P4.4  ──── depends on P3.1
P4.2  ──── depends on P2.1, P3.1, P4.1
P4.3  ──── depends on P2.1, P3.1, P4.1
P4.5  ──── depends on P4.1, P4.2, P4.3, P4.4
        │
P5.1  ──┐
P5.2  ─┤
P5.3  ─┤── depends on P4.5 (clean once v2 ships)
P5.4  ─┘
```

## Suggested parallel batches

The user can run multiple agents in parallel within each batch, then verify on-device before moving on.

| Batch | Tasks | Notes |
|---|---|---|
| **A** | P1.1, P1.2, P1.3, P1.4, P1.6 | All file-creation or isolated refactors. Fully parallel. |
| **B** | P1.5, P1.7 | After A. Each touches separate files. Parallel. |
| **C** | P2.1, P3.1 | After A. New files; parallel. |
| **D** | P3.2 | After B + C. Integration step — single agent. |
| **E** | P4.1, P4.4 | After C + P1.4. Parallel. |
| **F** | P4.2, P4.3 | After E + P2.1. Parallel. |
| **G** | P4.5 | After F. Integration step — single agent. |
| **H** | P5.1, P5.2, P5.3 | After G. Parallel deletions. |
| **I** | P5.4 | After H. CLAUDE.md rewrite. |

---

## Task list

### Phase 1 — Foundation (no behaviour change)
- [P1.1 — Add .gitignore](P1.1-gitignore.md)
- [P1.2 — Create settings.example.toml](P1.2-settings-example.md)
- [P1.3 — Build utils/touch.py](P1.3-touch-utility.md)
- [P1.4 — Build utils/config.py](P1.4-config-module.md)
- [P1.5 — Refactor TouchButton to use touch.normalize](P1.5-touchbutton-refactor.md)
- [P1.6 — Refactor SendRequest to DI + (ok, body) returns](P1.6-sendrequest-di.md)
- [P1.7 — Adapt code.py + existing screens to new SendRequest shape](P1.7-adapt-v1-to-sendrequest.md)

### Phase 2 — Components
- [P2.1 — Build components/CardButton.py](P2.1-cardbutton.md)

### Phase 3 — Navigator
- [P3.1 — Build utils/Navigator.py](P3.1-navigator.md)
- [P3.2 — Migrate code.py main loop to Navigator (still on v1 screens)](P3.2-migrate-mainloop.md)

### Phase 4 — New screens
- [P4.1 — Build screens/SuccessScreen.py](P4.1-successscreen.md)
- [P4.2 — Build screens/HomeScreen.py](P4.2-homescreen.md)
- [P4.3 — Build screens/AnnouncementScreen.py](P4.3-announcementscreen.md)
- [P4.4 — Build screens/NoConnectionScreen.py](P4.4-noconnectionscreen.md)
- [P4.5 — Wire v2 screens into Navigator and switch boot to home](P4.5-wire-v2-screens.md)

### Phase 5 — Cleanup
- [P5.1 — Delete MenuScreen, BroadcastScreen, ReactScreen](P5.1-delete-v1-screens.md)
- [P5.2 — Delete WeatherManager and weather state](P5.2-delete-weather.md)
- [P5.3 — Remove unused BMPs and react webhook config](P5.3-cleanup-bmps.md)
- [P5.4 — Update CLAUDE.md to point at v2 architecture](P5.4-update-claudemd.md)

### Out-of-band
- [Open questions](open-questions.md) — resolve these before P4.2 / P4.3 / P4.4
