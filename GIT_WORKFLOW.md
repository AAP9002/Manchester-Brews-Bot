
# Git workflow

Rules for Claude (and humans) when committing to this repo. The goal is a clean, bisectable history of small, reviewable changes — never one giant "did the thing" commit.

## Core principles

1. **One sub-task per branch.** Never commit directly to `main`. Cut a branch off `main` for each discrete piece of work.
2. **Small, atomic commits.** Each commit should do one thing and leave the repo in a working state. If the subject needs the word "and", split it.
3. **Conventional Commits, imperative mood.** Subjects describe what the change does, not what you did.
4. **Confirm before pushing or merging.** Local commits are reversible; pushed commits and merged PRs are not. Ask the user before `git push`, `git merge`, or opening a PR unless they have explicitly authorised it for the current task.

## Branch workflow

### Naming

`type/short-kebab-description` — type matches the Conventional Commit type:

- `feat/weather-cache`
- `fix/touch-rotation-react-screen`
- `refactor/screen-base-class`
- `docs/git-workflow`
- `chore/gitignore-secrets`

Keep the slug under ~40 chars. No issue numbers unless the project starts using them.

### Lifecycle

```
git checkout main
git pull --ff-only          # only if a remote exists
git checkout -b feat/weather-cache
# ... small commits ...
# when the sub-task is done, ASK the user before merging or pushing
```

- **Always branch from an up-to-date `main`.** If `main` has moved while you worked, rebase (`git rebase main`) — do not merge `main` into the feature branch.
- **One sub-task = one branch = one logical change.** If mid-task you discover an unrelated fix, stash or note it and do it on its own branch afterwards.
- **Don't delete branches** without confirming with the user, even after merge.

## Commit messages

### Format

```
<type>(<scope>): <subject>

<body — optional, wrap at 72 cols>

<footer — optional>
```

### Types

| Type       | Use for                                                       |
|------------|---------------------------------------------------------------|
| `feat`     | New user-visible behaviour                                    |
| `fix`      | Bug fix                                                       |
| `refactor` | Restructure without behaviour change                          |
| `docs`     | Markdown, comments, README, this file                         |
| `chore`    | Tooling, deps, `.gitignore`, build/deploy scripts             |
| `style`    | Whitespace/formatting only — no logic change                  |
| `perf`     | Measurable performance improvement                            |
| `test`     | Adding or fixing tests (n/a here until tests exist)           |

### Scope (optional but encouraged)

The screen, module, or subsystem touched. Examples for this repo: `weather`, `slack`, `menu-screen`, `react-screen`, `touch`, `state`, `settings`, `deploy`.

### Subject rules

- Imperative: "add", "fix", "remove" — not "added"/"adds".
- No trailing period.
- Lowercase after the colon.
- ≤ 72 chars total. If you need more, the subject is doing too much — split the commit.

### Body — when to include one

Add a body when the **why** is non-obvious. Skip it when the subject is self-explanatory.

Good body content:
- The constraint or bug that motivated the change.
- Trade-offs considered and why this option won.
- Anything a future reader would need to understand the diff.

Don't restate what the diff already shows.

### Examples

```
feat(weather): cache last forecast across reboots

Open-Meteo rate-limits aggressively when the device reboots in a loop
during development. Persist the last response to /sd/weather.json and
reuse it if the API call fails.
```

```
fix(touch): apply 90° rotation in MenuScreen.isPlusOnePressed

Hit-test was using raw CST8xx coords; +1 button only fired in the
top-right quadrant. Match the rotation already done in TouchButton.
```

```
refactor(screens): extract Screen base class

No behaviour change. Pulls get_screen / is_button_pressed /
fire_button_callback up so adding a new screen is one subclass.
```

```
chore: add .gitignore for settings.toml and boot_out.txt
```

## What belongs in one commit

A commit should answer **one** question. If the diff spans multiple answers, split it.

**Split when you see:**
- A refactor mixed with a behaviour change → refactor first, then the change on top.
- Two unrelated bug fixes → two commits.
- "Move file + edit file" → move in one commit (pure rename), edit in the next, so `git log --follow` works.
- New feature + unrelated formatting cleanup → cleanup goes on its own branch.

**Use `git add -p`** to stage hunks selectively when a working tree has grown beyond one logical change.

## Before every commit

1. `git status` — confirm only intended files are staged.
2. `git diff --staged` — read the diff you are about to commit.
3. **Never stage `settings.toml`** — it contains live WiFi password and Slack webhook URLs. If it appears in `git status` and isn't yet gitignored, stop and add it to `.gitignore` first.
4. **Never stage `boot_out.txt`** — written by CircuitPython on boot, churns on every deploy.
5. Subject reads as a complete sentence after "This commit will…".

## Don'ts

- ❌ Don't `git add -A` or `git add .` — name the files. Bulk-add is how secrets and `boot_out.txt` end up in history.
- ❌ Don't `--amend` a commit that has been pushed or shared.
- ❌ Don't `--no-verify` to skip hooks.
- ❌ Don't force-push `main`. Force-push to a feature branch only after telling the user.
- ❌ Don't rewrite history that has been pushed without explicit confirmation.
- ❌ Don't commit commented-out code or `print()` debug lines — remove them first.
- ❌ Don't mix "what" and "why" in the subject. The subject is the what; the body is the why.

## Sub-task sizing rule of thumb

If a branch produces more than ~5 commits or touches more than ~5 files, the sub-task was too big — next time, split it earlier. The fix once you're already there is to land what's done, branch again, continue.

## Repo-specific notes

- The project has **no test suite and no CI**. "Working state" means *the device boots and the affected screen still renders* — verify on-device before declaring a commit done where practical.
- `lib/` contains vendored Adafruit `.mpy` bundles. Treat library upgrades as their own `chore(lib): bump adafruit_<x> to <ver>` commit, separate from any code that uses the new version.
- The Bruno collection in `bruno/` is checked-in tooling — changes there are `chore(bruno): …`.
