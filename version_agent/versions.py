"""Version detection — reads pinned, installed, and latest versions."""

import re
import subprocess
import sys

from .config import PACKAGE_NAME, PINNED_VERSION_FILE


def get_current_pinned_version() -> str:
    """Read the currently pinned version from pinned_version.txt."""
    return PINNED_VERSION_FILE.read_text().strip()


def get_installed_version() -> str:
    """Get the version currently installed via pip."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", PACKAGE_NAME],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return ""


def get_latest_version() -> str:
    """Query PyPI for the latest available version."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "index", "versions", PACKAGE_NAME],
        capture_output=True, text=True
    )
    match = re.search(r"\((\d+\.\d+\.\d+)\)", result.stdout)
    return match.group(1) if match else ""
