"""Profile management — list and validate notebooklm-py profiles."""

from pathlib import Path


NOTEBOOKLM_HOME = Path.home() / ".notebooklm" / "profiles"


def list_profiles() -> list[str]:
    """Return a list of configured profile names."""
    if not NOTEBOOKLM_HOME.exists():
        return []
    return [
        p.name for p in NOTEBOOKLM_HOME.iterdir()
        if p.is_dir() and (p / "storage_state.json").exists()
    ]


def profile_exists(name: str) -> bool:
    """Check if a specific profile has been authenticated."""
    return (NOTEBOOKLM_HOME / name / "storage_state.json").exists()
