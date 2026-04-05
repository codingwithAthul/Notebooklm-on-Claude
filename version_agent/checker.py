"""API blocker detection — scans GitHub releases and issues for red flags."""

import json
import subprocess

from .config import API_BLOCKER_KEYWORDS, GITHUB_REPO


def fetch_release_notes(version: str) -> str:
    """Fetch release notes from GitHub for a specific version tag."""
    for tag in [f"v{version}", version]:
        try:
            result = subprocess.run(
                ["curl", "-s", f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{tag}"],
                capture_output=True, text=True, timeout=30
            )
            data = json.loads(result.stdout)
            body = data.get("body", "")
            if body:
                return body
        except Exception:
            continue
    return ""


def fetch_recent_issues() -> list[dict]:
    """Fetch recent open issues from GitHub to check for blocker reports."""
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
    Scan release notes and recent issues for signs of Google API blockers.
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
        return True, "; ".join(reasons[:3])
    return False, ""
