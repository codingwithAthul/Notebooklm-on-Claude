# NotebookLM Workspace

A workspace for integrating [Google NotebookLM](https://notebooklm.google.com/) with [Claude Code](https://claude.ai/code) via the unofficial [`notebooklm-py`](https://github.com/teng-lin/notebooklm-py) Python wrapper — with built-in automated version management and API safety checks.

## What This Project Does

- **Sets up NotebookLM** for use inside Claude Code on your local machine
- **Pins the dependency version** to protect against unexpected breaking changes
- **Automates weekly update checks** via a version agent that:
  - Queries PyPI for new `notebooklm-py` releases
  - Scans GitHub release notes and open issues for signs that Google has blocked or broken the unofficial API
  - Only updates if no API blockers are detected
  - Logs all activity for auditability

## Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Playwright** (for browser-based Google authentication)
- **macOS** (for the launchd-based weekly scheduler — see [Scheduling on Other OS](#scheduling-on-other-os) for alternatives)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/codingwithAthul/Notebooklm-on-Claude.git
cd Notebooklm-on-Claude
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs `notebooklm-py[browser]==0.3.4` (pinned) and `playwright`.

### 3. Install Chromium for Playwright

```bash
playwright install chromium
```

### 4. Authenticate with Google

```bash
notebooklm login
```

This opens a real Chromium browser window. Log into your Google account directly on Google's page. The library only captures the resulting session cookies after login — **your password is never seen or handled by the library**.

Your session cookies are stored locally at `~/.notebooklm/` with owner-only permissions (`0o600`).

### 5. Verify the setup

```bash
python3 run_agent.py
```

You should see output like:

```
[2026-04-04 10:23:00] === Version Agent Check Started ===
[2026-04-04 10:23:02] Pinned: 0.3.4 | Installed: 0.3.4 | Latest: 0.3.4
[2026-04-04 10:23:02] Already on latest version. No update needed.
```

## Project Structure

```
Notebooklm-on-Claude/
├── .gitignore              # Excludes auth cookies, logs, Python cache
├── requirements.txt        # Pinned dependency: notebooklm-py[browser]==0.3.4
├── pinned_version.txt      # Tracks current active version (read/written by agent)
├── run_agent.py            # Root-level entry point for launchd/cron
└── version_agent/          # Version management package
    ├── __init__.py         # Package metadata
    ├── __main__.py         # Orchestrates the full check-and-update flow
    ├── config.py           # Constants, file paths, API blocker keywords
    ├── logger.py           # Timestamped logging to file and stdout
    ├── versions.py         # Detects pinned, installed, and latest versions
    ├── checker.py          # Scans GitHub for API blockers before updating
    └── updater.py          # Performs safe pip install and updates tracking files
```

## How the Version Agent Works

The version agent runs a safety-first update flow:

```
1. Read pinned version from pinned_version.txt
2. Query pip for currently installed version
3. Query PyPI for latest available version
4. If latest == pinned → no action needed
5. If latest != pinned →
   a. Fetch GitHub release notes for the new version
   b. Fetch recent open issues from the GitHub repo
   c. Scan both for API blocker keywords:
      "blocked", "auth broken", "403", "breaking change",
      "google block", "captcha", "endpoint changed", etc.
   d. If blockers found → SKIP update, log the reason
   e. If clean → install new version, update pinned_version.txt
      and requirements.txt
6. Log everything to logs/version_agent.log
```

You can run it manually at any time:

```bash
# From the project root
python3 run_agent.py

# Or as a Python module
python3 -m version_agent
```

## Setting Up the Weekly Scheduler (macOS launchd)

The version agent is designed to run automatically every week. On macOS, the recommended approach is `launchd`, which:

- Survives reboots and session restarts
- Runs missed jobs after sleep/wake (unlike cron)
- Runs as your user without root access

### Create the launchd plist

Create the file `~/Library/LaunchAgents/com.notebooklm.versionagent.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.notebooklm.versionagent</string>

    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/python3</string>
        <string>/path/to/Notebooklm-on-Claude/run_agent.py</string>
    </array>

    <!-- Run every Saturday at 10:23 AM -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>6</integer>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>23</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/path/to/Notebooklm-on-Claude/logs/launchd_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/Notebooklm-on-Claude/logs/launchd_stderr.log</string>
</dict>
</plist>
```

Replace `/path/to/your/python3` and `/path/to/Notebooklm-on-Claude/` with your actual paths.

To find your Python path: `which python3`

### Load the agent

```bash
launchctl load ~/Library/LaunchAgents/com.notebooklm.versionagent.plist
```

### Useful commands

```bash
# Check if the agent is registered
launchctl list | grep notebooklm

# Manually trigger a run
launchctl start com.notebooklm.versionagent

# Stop the agent
launchctl unload ~/Library/LaunchAgents/com.notebooklm.versionagent.plist

# Reload after editing the plist
launchctl unload ~/Library/LaunchAgents/com.notebooklm.versionagent.plist
launchctl load ~/Library/LaunchAgents/com.notebooklm.versionagent.plist
```

### Scheduling on Other OS

**Linux (crontab):**

```bash
crontab -e
# Add:
23 10 * * 6 /usr/bin/python3 /path/to/Notebooklm-on-Claude/run_agent.py >> /path/to/Notebooklm-on-Claude/logs/cron.log 2>&1
```

**Windows (Task Scheduler):**

Create a scheduled task that runs `python run_agent.py` weekly using Windows Task Scheduler.

## Security Notes

### About notebooklm-py

- This is an **unofficial** wrapper around undocumented Google NotebookLM APIs — it is not affiliated with Google
- Google could change or block these APIs at any time (which is why the version agent exists)
- All network requests go **exclusively to Google domains** — no telemetry or third-party data transmission
- Your Google password is **never handled** by the library — you authenticate directly with Google via a real browser

### Authentication safety

- Session cookies are stored at `~/.notebooklm/` with `0o600` permissions (owner-only)
- **Never commit `~/.notebooklm/` to version control** — it contains Google session cookies that could be used to impersonate your account
- The `.gitignore` in this repo excludes auth-related files as a safety net
- You can revoke sessions at any time via [Google Security Settings](https://myaccount.google.com/permissions)

### Version pinning

- The dependency is pinned to a specific version (`0.3.4`) in `requirements.txt`
- The version agent only upgrades after verifying no API blockers exist
- To manually pin a different version: update both `requirements.txt` and `pinned_version.txt`
