"""Package updater — handles safe version upgrades."""

import subprocess
import sys

from .config import PACKAGE_NAME, PINNED_VERSION_FILE, REQUIREMENTS_FILE


def update_package(version: str):
    """Install a specific version and update the pinned version tracking files."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", f"{PACKAGE_NAME}[browser]=={version}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"pip install failed: {result.stderr}")

    PINNED_VERSION_FILE.write_text(f"{version}\n")
    REQUIREMENTS_FILE.write_text(
        f"notebooklm-py[browser]=={version}\nplaywright>=1.40.0\n"
    )
