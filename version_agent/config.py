"""Configuration constants and file paths for the version agent."""

from pathlib import Path

PACKAGE_NAME = "notebooklm-py"
GITHUB_REPO = "teng-lin/notebooklm-py"

WORKSPACE = Path(__file__).resolve().parent.parent
PINNED_VERSION_FILE = WORKSPACE / "pinned_version.txt"
PREVIOUS_VERSION_FILE = WORKSPACE / "previous_version.txt"
REQUIREMENTS_FILE = WORKSPACE / "requirements.txt"
LOG_DIR = WORKSPACE / "logs"

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
