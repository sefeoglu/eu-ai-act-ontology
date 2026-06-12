"""Utility helpers for local file-path handling."""

from pathlib import Path

<<<<<<< HEAD
=======

>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def data_path(*parts: str) -> Path:
    """Return an absolute path under the repository data directory."""
    return PROJECT_ROOT / "data" / Path(*parts)


def ensure_file_exists(path: Path) -> Path:
<<<<<<< HEAD
    """Validate that a path exists and return it."""
=======
    """Validate a path exists and return it."""
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path
