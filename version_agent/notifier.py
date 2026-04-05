"""macOS native notifications for version agent events."""

import platform
import subprocess


def notify(title: str, message: str):
    """Send a macOS notification. Silently no-ops on other platforms."""
    if platform.system() != "Darwin":
        return

    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, timeout=10
        )
    except Exception:
        pass  # Notification is best-effort, never block the agent
