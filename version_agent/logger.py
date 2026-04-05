"""Logging utility for the version agent."""

from datetime import datetime

from .config import LOG_DIR


def log(message: str):
    """Write a timestamped log entry to file and stdout."""
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / "version_agent.log"
    entry = f"[{timestamp}] {message}\n"
    with open(log_file, "a") as f:
        f.write(entry)
    print(entry.strip())
