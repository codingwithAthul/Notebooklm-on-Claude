"""Package updater — handles safe version upgrades and rollbacks."""

import subprocess
import sys

from .config import PACKAGE_NAME, PINNED_VERSION_FILE, PREVIOUS_VERSION_FILE, REQUIREMENTS_FILE


def _write_version_files(version: str):
    """Update pinned_version.txt and requirements.txt to a given version."""
    PINNED_VERSION_FILE.write_text(f"{version}\n")
    REQUIREMENTS_FILE.write_text(
        f"notebooklm-py[browser]=={version}\nplaywright>=1.40.0\n"
    )


def _pip_install(version: str):
    """Run pip install for a specific version. Raises RuntimeError on failure."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", f"{PACKAGE_NAME}[browser]=={version}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"pip install failed: {result.stderr}")


def smoke_test() -> bool:
    """Verify the installed notebooklm package can be imported."""
    result = subprocess.run(
        [sys.executable, "-c", "import notebooklm; print(notebooklm.__version__)"],
        capture_output=True, text=True
    )
    return result.returncode == 0


def update_package(version: str, current_version: str):
    """Install a new version with backup of the current version for rollback.

    Saves the current version to previous_version.txt before upgrading.
    After install, runs a smoke test — auto-rolls back if it fails.
    """
    # Save current version for rollback
    PREVIOUS_VERSION_FILE.write_text(f"{current_version}\n")

    _pip_install(version)
    _write_version_files(version)

    # Smoke test: verify the new version can be imported
    if not smoke_test():
        raise RuntimeError(
            f"Smoke test failed after updating to {version}. "
            f"Run 'python -m version_agent --rollback' to revert."
        )


def rollback() -> str:
    """Roll back to the previous version saved in previous_version.txt.

    Returns the version that was restored.
    Raises FileNotFoundError if no previous version exists.
    Raises RuntimeError if pip install fails.
    """
    if not PREVIOUS_VERSION_FILE.exists():
        raise FileNotFoundError("No previous version found. Nothing to roll back to.")

    previous = PREVIOUS_VERSION_FILE.read_text().strip()
    if not previous:
        raise FileNotFoundError("previous_version.txt is empty. Nothing to roll back to.")

    _pip_install(previous)
    _write_version_files(previous)

    return previous
