"""Entry point for the version agent — run with: python -m version_agent"""

import sys

from .checker import check_for_api_blockers
from .logger import log
from .notifier import notify
from .profiles import list_profiles
from .updater import rollback, update_package
from .versions import get_current_pinned_version, get_installed_version, get_latest_version


def handle_rollback():
    """Handle the --rollback command."""
    log("=== Rollback Requested ===")
    try:
        previous = rollback()
        log(f"Successfully rolled back to {previous}")
    except FileNotFoundError as e:
        log(f"ROLLBACK FAILED: {e}")
    except RuntimeError as e:
        log(f"ROLLBACK ERROR: {e}")


def handle_profiles():
    """Handle the --profiles command."""
    profiles = list_profiles()
    if not profiles:
        print("No authenticated profiles found.")
        print("Run 'notebooklm login --profile <name>' to create one.")
        return
    print(f"Authenticated profiles ({len(profiles)}):")
    for name in profiles:
        print(f"  - {name}")


def main():
    # Handle --profiles flag
    if "--profiles" in sys.argv:
        handle_profiles()
        return

    # Handle --rollback flag
    if "--rollback" in sys.argv:
        handle_rollback()
        return

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
        notify("NotebookLM Update Blocked", f"v{latest} blocked: {reason[:80]}")
        return

    log(f"No API blockers found. Updating to {latest}...")
    try:
        update_package(latest, current)
        log(f"Successfully updated to {latest}")
        notify("NotebookLM Updated", f"v{current} → v{latest}")
    except RuntimeError as e:
        log(f"ERROR: {e}")
        notify("NotebookLM Update Failed", f"v{latest} failed — rolling back")
        log(f"Auto-rolling back to {current}...")
        try:
            rollback()
            log(f"Successfully rolled back to {current}")
        except (FileNotFoundError, RuntimeError) as rb_err:
            log(f"ROLLBACK ALSO FAILED: {rb_err}")
            notify("NotebookLM Rollback Failed", f"Manual intervention needed")


if __name__ == "__main__":
    main()
