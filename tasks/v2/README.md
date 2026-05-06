# Coffee Bot v2 — Task Index

Self-contained task files for the v2 refactor. Each `.md` here can be handed to an independent agent without conversation context — read the file, read the linked HLD sections, do the work, mark it done.

**Authoritative architecture reference:** `../../V2-ARCHITECTURE.md` (project root).

---

## For the orchestrator (kicking off agents)

This directory is designed to be sub-agent-friendly. Each task file is self-contained: an agent given only the path can read it, do the work, and update its status without seeing this README or the conversation that produced the plan.

### Before launching the first agent

- [ ] **v1 works on-device.** Verify the current build boots and every flow works. Establishes the baseline.
- [ ] **Clean git state.** Either run P1.1 manually first or have the first agent do it, then `git commit -m "v1 baseline"` immediately. This is the rollback point.
- [ ] **Confirm env-var key names in `settings.toml`** match what the screen tasks reference (`LOW_ON_BEANS_WEBHOOK`, `BREWING_WEBHOOK`, `READY_WEBHOOK`, `SEND_MESSAGE_SLACK_WEBHOOK`, `GOOGLE_SHEET_URL`). Reconcile once so no agent has to guess.
- [ ] **Resolve as many entries in `open-questions.md` as possible.** Especially Q1 (export the three new card BMPs) and Q2 (hard-code "Alex" or expose as env var).
- [ ] **Verify `deploy.sh` and `/Volumes/CIRCUITPY`** are working — agents complete code work, but you (or you running deploy.sh in a side terminal) push it to the device for verification.

### Agent prompt template

Paste this into the Agent tool (or main Claude session), substituting the task path:

```
Read tasks/v2/P1.X-NAME.md and complete the task it describes.

Hard rules:
1. Stay strictly within the task's "Files to touch" list. Do not modify or read
   files outside that scope unless the task explicitly tells you to.
2. Do not expand scope. If you hit something that requires touching more files
   or making decisions outside the spec, STOP and append a "## Notes" section
   to the task file describing what you found, then return.
3. The architectural reference is V2-ARCHITECTURE.md at the project root.
   Read only the sections the task points to plus any source files it names.
4. Verify your work against the "Acceptance criteria" checklist before
   declaring done.
5. When complete, update the top-of-file "Status:" from "not-started" to
   "done" (or "blocked" with a Notes section if you cannot complete it).

Do NOT run the device or attempt on-device verification — the user does that
between agent runs. Do NOT git commit or push.
```

### Running batches in parallel

The "Suggested parallel batches" table below lists tasks that touch disjoint files. For Batch A, every task creates a separate new file or touches an isolated existing one — fully safe to run concurrently.

In a single Claude Code message, dispatch multiple agents at once by issuing several `Agent` tool calls in the same response. Example for Batch A:

```
Agent({ prompt: "<template>", description: "P1.1 gitignore" })
Agent({ prompt: "<template>", description: "P1.2 settings example" })
Agent({ prompt: "<template>", description: "P1.3 touch utility" })
Agent({ prompt: "<template>", description: "P1.4 config module" })
Agent({ prompt: "<template>", description: "P1.6 sendrequest DI" })
Agent({ prompt: "<template>", description: "P1.8 layout module" })
```

For batches with overlapping files (P1.7, P3.2, P4.5), prefer **one agent at a time** in the shared workspace, or pass `isolation: "worktree"` so each agent works on its own copy and you merge afterwards.

### Between batches

1. **Verify on-device.** Each task has an "On-device verification" or "Verify" checkbox. If a task changed runtime behaviour, deploy and exercise the relevant flow before launching the next batch.
2. **Commit.** Lock in working state. Agents can then be safely launched against the next batch with a known-good rollback point.
3. **Check for `## Notes` sections** the agents may have appended — these flag scope boundaries that need your decision before the next batch.

---

## For an agent picking up a task

1. Confirm your task's `Depends on` list is fully satisfied (all listed tasks marked `done` in their own files).
2. Read the task file end-to-end — `Context`, `Files to touch`, `Specification`, `Acceptance criteria`, `Out of scope`.
3. Read the HLD sections the task references.
4. Read the source files the task names.
5. Do the work. Stay inside the task's stated scope — do not refactor neighbouring code.
6. Update the `Status:` line at the top of the task file from `not-started` → `done` (or `blocked` with details).
7. **Do not run the device.** The orchestrator handles on-device verification between runs.

If the task uncovers a problem that can't be solved without expanding scope, stop and write the issue under a `## Notes` section at the bottom of the task file rather than silently growing the change.

---

## Dependency graph

```
P1.1  ─┐
P1.2  ─┤
P1.3  ─┤
P1.4  ─┼── (parallel batch A — no dependencies)
P1.6  ─┤
P1.8  ─┘
        │
P1.5  ──── depends on P1.3
P1.7  ──── depends on P1.6
        │
P2.1  ──── depends on P1.3, P1.4, P1.8
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
| **A** | P1.1, P1.2, P1.3, P1.4, P1.6, P1.8 | All file-creation or isolated refactors. Fully parallel. |
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
- [P1.3 — Build utils/touch.py (normalize + TouchTracker)](P1.3-touch-utility.md)
- [P1.4 — Build utils/config.py](P1.4-config-module.md)
- [P1.5 — Refactor TouchButton to use touch.normalize](P1.5-touchbutton-refactor.md)
- [P1.6 — Refactor SendRequest to DI + (ok, body) returns](P1.6-sendrequest-di.md)
- [P1.7 — Adapt code.py + existing screens to new SendRequest shape](P1.7-adapt-v1-to-sendrequest.md)
- [P1.8 — Build utils/layout.py (text + layout primitives)](P1.8-layout-module.md)

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
