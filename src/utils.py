"""Utility helpers for local file-path handling."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def data_path(*parts: str) -> Path:
    """Return an absolute path under the repository data directory."""
    return PROJECT_ROOT / "data" / Path(*parts)


def ensure_file_exists(path: Path) -> Path:
    """Validate that a path exists and return it."""
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path
