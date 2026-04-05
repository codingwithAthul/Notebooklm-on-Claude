# Project Progress — Notebooklm-on-Claude

Last updated: 2026-04-05

---

## What This Project Is

A workspace for integrating Google NotebookLM with Claude Code via the unofficial `notebooklm-py` Python wrapper. Includes automated version management, API safety checks, and a weekly update scheduler.

**Repo:** [codingwithAthul/Notebooklm-on-Claude](https://github.com/codingwithAthul/Notebooklm-on-Claude)

---

## What Was Done (2026-04-04 — 2026-04-05)

### Session 1 — Initial setup (April 4)

1. **Research and security audit** — Investigated the `notebooklm-py` package (by `teng-lin`) for safety. Confirmed: all network requests go exclusively to Google domains, no telemetry, password never handled by the library, session cookies stored locally with `0o600` permissions.

2. **Installed `notebooklm-py[browser]==0.3.4`** — Pinned version in `requirements.txt` to protect against breaking changes from upstream.

3. **Built the version agent** (`version_agent/` package) — Automated update manager that:
   - Queries PyPI for latest `notebooklm-py` version
   - Scans GitHub release notes and open issues for API blocker keywords (e.g., "blocked", "403", "auth broken", "breaking change")
   - Only updates if no blockers are detected
   - Runs a smoke test (import check) after updating
   - Auto-rolls back to the previous version if the smoke test fails
   - Sends macOS desktop notifications on update/block/failure events
   - Supports manual rollback via `--rollback` flag
   - Supports listing authenticated Google profiles via `--profiles` flag
   - Logs all activity to `logs/version_agent.log`

4. **Set up macOS `launchd` scheduler** — Created `com.notebooklm.versionagent` plist at `~/Library/LaunchAgents/` to run the version agent every Saturday at 10:23 AM. Chose launchd over cron because it survives reboots, handles sleep/wake, and runs missed jobs.

5. **Created GitHub-Manager skill** — Custom Claude Code skill (`.claude/skills/github-manager/SKILL.md`) that standardizes all GitHub operations: semantic branch naming, conventional commits, commit-per-file rule, dev/main branching strategy, PR conventions.

6. **Uploaded project to GitHub** — Created the repo with `main` → `dev` → feature branch workflow. Each file committed individually with semantic messages. Total of 18 PRs and 30+ commits across multiple feature branches.

### Session 2 — Feature additions (April 5)

7. **Added rollback support** (PR #13, Issue #9) — Saves current version to `previous_version.txt` before updating. Auto-rolls back if smoke test fails. Manual rollback via `python3 -m version_agent --rollback`.

8. **Added macOS desktop notifications** (PR #14, Issue #8) — Native notifications via `osascript` for update blocked, success, failure, and rollback failure events.

9. **Added multi-profile support** (PR #15, Issue #6) — `profiles.py` module to list and validate authenticated Google profiles. `--profiles` CLI flag. README guide for multiple accounts.

10. **Added CHANGELOG.md** (PR #12, Issue #7) — Following Keep a Changelog format. Documents v1.0.0 and v1.1.0.

11. **Released v1.0.0 and v1.1.0** — Created git tags and GitHub releases. Merged dev to main for release.

12. **Renamed project** (PR #10) — From `notebooklm-workspace` to `Notebooklm-on-Claude`. Updated all 14 references (README, remote URL, launchd plist, etc.).

13. **Git history cleanup** — Removed Claude Code co-author attribution from all commits. Rewrote history so all commits appear user-authored.

### Session 3 — Example scripts (April 5, current)

14. **Authenticated with Google** — Ran `notebooklm login`, confirmed session cookies saved at `~/.notebooklm/storage_state.json`.

15. **Created and live-tested 4 example scripts** (PR #18, Issue #5 — still open):
    - `examples/list_notebooks.py` — Lists all notebooks with title, ID, source count, date, ownership. Tested against 8 existing notebooks.
    - `examples/create_notebook.py` — Creates a notebook, adds a text source and a URL source (Wikipedia). Verified both sources processed successfully.
    - `examples/ask_notebook.py` — Asks questions to a notebook with follow-up conversation support using `conversation_id`. Tested with real Q&A.
    - `examples/manage_sources.py` — Demonstrates add, rename, and delete operations on sources. Verified full lifecycle.
    - Cleaned up the demo notebook after testing.

16. **Updated README and CHANGELOG** — Added example scripts section, updated project structure tree, added v1.2.0 changelog entry.

---

## Key Technical Decisions

| Decision | Why |
|---|---|
| Pinned `notebooklm-py==0.3.4` | Unofficial API — Google can break it at any time. Pinning prevents silent breakage. |
| Version agent scans GitHub before updating | API blocker keywords in release notes or issues = skip the update. Safety first. |
| Smoke test + auto-rollback after install | Even if no blockers detected, the new version might not work. Import check catches that. |
| `launchd` instead of `cron` | macOS cron doesn't handle sleep/wake or missed jobs. launchd does. |
| `dev` → `main` branching strategy | `main` is release-only. All work goes through `dev` via feature branches and PRs. |
| Commit per file, semantic messages | Granular git history. Easy to revert individual changes. |
| Async `NotebookLMClient` | The `notebooklm-py` library uses an async API with `asyncio`. All example scripts follow `async with await NotebookLMClient.from_storage() as client:` pattern. |
| `.kind` instead of `.source_type` | `.source_type` is deprecated in v0.3.4, will be removed in v0.4.0. |

---

## Current State

- **Latest release:** v1.1.0 (on `main`)
- **Open PR:** #18 — `feat/example-scripts` → `dev` (4 example scripts, README/CHANGELOG updates)
- **Open Issue:** #5 — "feat: Add example NotebookLM usage scripts"
- **Closed Issues:** #6, #7, #8, #9
- **Total PRs:** 18 (17 merged, 1 open)
- **launchd agent:** Active, running weekly Saturdays at 10:23 AM
- **Authentication:** Google session active at `~/.notebooklm/storage_state.json`
- **Package:** `notebooklm-py[browser]==0.3.4` installed and working

### Files on `feat/example-scripts` branch (not yet on main)

```
examples/
├── list_notebooks.py    # List all notebooks
├── create_notebook.py   # Create notebook + add sources
├── ask_notebook.py      # Query notebook with follow-ups
└── manage_sources.py    # Add, rename, delete sources
```

---

## Next Steps

### Immediate (before merging PR #18)

The user wants to **manually test more NotebookLM use cases** before deciding what example scripts to finalize. The current 4 scripts are live-tested and working, but the user may want to:

- Add more scripts covering additional API features (artifacts/audio generation, notes, sharing, research, settings)
- Modify existing scripts based on real-world usage patterns
- Remove or restructure scripts that don't feel useful in practice

**Action:** User tests NotebookLM manually → evaluates quality → provides finer instructions on what to keep, change, or add → then we finalize PR #18 and merge.

### Future ideas (not committed to)

- **More example scripts** — The `notebooklm-py` API has many more features:
  - `client.artifacts` — Generate audio overviews, podcasts, study guides, reports, slide decks, infographics, videos
  - `client.notes` — Create and manage user notes within notebooks
  - `client.sharing` — Share notebooks with other users
  - `client.research` — Web/Drive research sessions
  - `client.settings` — User settings (output language, etc.)
- **Integration patterns** — Scripts showing how to use NotebookLM within a Claude Code workflow (e.g., "upload this codebase to a notebook and ask it questions")
- **Error handling examples** — Demonstrating how to handle auth expiry, rate limits, source processing failures
- **v1.2.0 release** — Once PR #18 is finalized and merged to dev → main

---

## Repository Structure (current main)

```
Notebooklm-on-Claude/
├── .gitignore
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── pinned_version.txt
├── run_agent.py
└── version_agent/
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── logger.py
    ├── versions.py
    ├── checker.py
    ├── updater.py
    ├── notifier.py
    └── profiles.py
```

---

## How to Resume This Project

1. Open Claude Code in `/Users/masterproject/Projects/Notebooklm-on-Claude/`
2. Read this file (`progress.md`) for full context
3. Check `git status` and `git branch` — should be on `feat/example-scripts`
4. PR #18 is open at https://github.com/codingwithAthul/Notebooklm-on-Claude/pull/18
5. Issue #5 is open at https://github.com/codingwithAthul/Notebooklm-on-Claude/issues/5
6. The GitHub-Manager skill is at `.claude/skills/github-manager/SKILL.md` — follow it for all git operations
7. If Google session has expired, re-authenticate with `notebooklm login`
