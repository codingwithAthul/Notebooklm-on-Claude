# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.2.0] - 2026-04-05

### Added
- **Example scripts** — `examples/` directory with four live-tested scripts: list notebooks, create notebook with sources, ask questions with follow-ups, manage sources (add/rename/delete) (#5)
- Updated README with example scripts section and project structure

## [1.1.0] - 2026-04-05

### Added
- **Rollback support** — saves current version to `previous_version.txt` before updating; auto-rolls back if smoke test (import check) fails after install; manual rollback via `python3 -m version_agent --rollback` (#9)
- **macOS desktop notifications** — sends native notifications on update blocked, update success, update failure, and rollback failure via `osascript` (#8)
- **Multi-profile support** — `profiles.py` module to list and validate authenticated Google profiles; `--profiles` CLI flag; README guide for setting up multiple accounts (#6)
- Updated README with new CLI commands, project structure, and version agent workflow reflecting smoke test and notifications

## [1.0.0] - 2026-04-04

### Added
- Project setup with pinned `notebooklm-py[browser]==0.3.4` dependency
- `version_agent/` Python package for automated update management
  - `config.py` — centralized constants, file paths, and API blocker keywords
  - `versions.py` — detects pinned, installed, and latest package versions via PyPI
  - `checker.py` — scans GitHub releases and open issues for API blocker signals
  - `updater.py` — safe package updater with version file sync
  - `logger.py` — timestamped logging to file and stdout
  - `__main__.py` — orchestrates the full check-and-update flow
- `run_agent.py` — root-level entry point for launchd/cron
- `pinned_version.txt` — tracks the currently active pinned version
- `.gitignore` — excludes auth cookies, Python cache, and logs
- Comprehensive `README.md` with:
  - Installation and authentication guide
  - Version agent workflow explanation
  - macOS launchd scheduling instructions (plus Linux/Windows alternatives)
  - Security notes on unofficial API and cookie safety

### Infrastructure
- macOS `launchd` agent (`com.notebooklm.versionagent`) for weekly automated checks
- GitHub repository with `main`/`dev` branching strategy
