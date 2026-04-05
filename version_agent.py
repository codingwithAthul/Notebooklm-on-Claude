#!/usr/bin/env python3
"""
Version Agent for notebooklm-py
Checks for new releases, inspects changelogs for API-blocking changes,
and auto-updates only if safe.

Runs weekly via cron/scheduler.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PACKAGE_NAME = "notebooklm-py"
WORKSPACE = Path(__file__).parent
PINNED_VERSION_FILE = WORKSPACE / "pinned_version.txt"
REQUIREMENTS_FILE = WORKSPACE / "requirements.txt"
LOG_DIR = WORKSPACE / "logs"
GITHUB_REPO = "teng-lin/notebooklm-py"

# Keywords that signal an API blocker or breaking change from Google
API_BLOCKER_KEYWORDS = [
    "blocked",
    "api break",
    "api change",
    "breaking change",
    "google block",
    "captcha",
    "rate limit",
    "authentication fail",
    "auth broken",
    "login broken",
    "403",
    "401",
    "deprecated endpoint",
    "endpoint changed",
    "batchexecute changed",
    "csrf changed",
    "blocked by google",
    "no longer works",
    "service unavailable",
]


def get_current_pinned_version() -> str:
    return PINNED_VERSION_FILE.read_text().strip()


def get_installed_version() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", PACKAGE_NAME],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return ""


def get_latest_version() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "index", "versions", PACKAGE_NAME],
        capture_output=True, text=True
    )
    # Output format: "notebooklm-py (0.3.4)"
    match = re.search(r"\((\d+\.\d+\.\d+)\)", result.stdout)
    return match.group(1) if match else ""


def fetch_release_notes(version: str) -> str:
    """Fetch release notes from GitHub for a specific version."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/v{version}"],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data.get("body", "")
    except Exception:
        pass

    # Also try without 'v' prefix
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}"],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data.get("body", "")
    except Exception:
        return ""


def fetch_recent_issues() -> list[dict]:
    """Fetch recent open issues to check for API blocker reports."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open&per_page=30"],
            capture_output=True, text=True, timeout=30
        )
        return json.loads(result.stdout)
    except Exception:
        return []


def check_for_api_blockers(version: str) -> tuple[bool, str]:
    """
    Check release notes and recent issues for signs of Google API blockers.
    Returns (is_blocked, reason).
    """
    reasons = []

    # Check release notes
    notes = fetch_release_notes(version)
    notes_lower = notes.lower()
    for keyword in API_BLOCKER_KEYWORDS:
        if keyword in notes_lower:
            reasons.append(f"Release notes contain '{keyword}'")

    # Check recent issues for API blocker reports
    issues = fetch_recent_issues()
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        title = (issue.get("title", "") or "").lower()
        labels = [l.get("name", "").lower() for l in issue.get("labels", []) if isinstance(l, dict)]

        for keyword in API_BLOCKER_KEYWORDS:
            if keyword in title:
                reasons.append(f"Open issue #{issue.get('number')}: {issue.get('title')}")
                break
        if "bug" in labels and any(kw in title for kw in ["auth", "login", "block", "break", "403", "401"]):
            reasons.append(f"Bug issue #{issue.get('number')}: {issue.get('title')}")

    if reasons:
        return True, "; ".join(reasons[:3])  # Cap at 3 reasons
    return False, ""


def update_package(version: str):
    """Install the new version and update pinned version file."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", f"{PACKAGE_NAME}[browser]=={version}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"pip install failed: {result.stderr}")

    # Update pinned version
    PINNED_VERSION_FILE.write_text(f"{version}\n")

    # Update requirements.txt
    REQUIREMENTS_FILE.write_text(
        f"notebooklm-py[browser]=={version}\nplaywright>=1.40.0\n"
    )


def log(message: str):
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / "version_agent.log"
    entry = f"[{timestamp}] {message}\n"
    with open(log_file, "a") as f:
        f.write(entry)
    print(entry.strip())


def main():
    log("=== Version Agent Check Started ===")

    current = get_current_pinned_version()
    installed = get_installed_version()
    latest = get_latest_version()

    log(f"Pinned: {current} | Installed: {installed} | Latest: {latest}")

    if not latest:
        log("ERROR: Could not determine latest version. Skipping.")
        return

    if latest == current:
        log("Already on latest version. No update needed.")
        return

    log(f"New version available: {latest} (current: {current})")

    # Check for API blockers
    is_blocked, reason = check_for_api_blockers(latest)

    if is_blocked:
        log(f"UPDATE BLOCKED - API blocker detected: {reason}")
        log(f"Staying on version {current}. Manual review recommended.")
        return

    # Safe to update
    log(f"No API blockers found. Updating to {latest}...")
    try:
        update_package(latest)
        log(f"Successfully updated to {latest}")
    except RuntimeError as e:
        log(f"ERROR: Update failed - {e}")


if __name__ == "__main__":
    main()
