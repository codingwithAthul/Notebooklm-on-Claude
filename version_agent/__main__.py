"""Entry point for the version agent — run with: python -m version_agent"""

from .checker import check_for_api_blockers
from .logger import log
from .updater import update_package
from .versions import get_current_pinned_version, get_installed_version, get_latest_version


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

    is_blocked, reason = check_for_api_blockers(latest)

    if is_blocked:
        log(f"UPDATE BLOCKED - API blocker detected: {reason}")
        log(f"Staying on version {current}. Manual review recommended.")
        return

    log(f"No API blockers found. Updating to {latest}...")
    try:
        update_package(latest)
        log(f"Successfully updated to {latest}")
    except RuntimeError as e:
        log(f"ERROR: Update failed - {e}")


if __name__ == "__main__":
    main()
