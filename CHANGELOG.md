# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
