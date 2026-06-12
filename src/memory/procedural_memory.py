<<<<<<< HEAD
"""Procedural memory: regulatory source-document metadata."""

from pathlib import Path
from typing import Any, Dict, Optional
=======
"""Procedural memory helpers for regulatory source artifacts."""

from pathlib import Path
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7

from src.utils import data_path, ensure_file_exists


class ProceduralMemory:
<<<<<<< HEAD
    """Tracks the procedural memory source document path and metadata."""

    DEFAULT_PATH: Path = data_path(
        "memory", "procedural_memory", "OJ_L_202401689_EN_TXT.pdf"
    )

    def __init__(self, document_path: Optional[Path] = None) -> None:
        resolved = Path(document_path) if document_path else self.DEFAULT_PATH
        self.document_path: Path = ensure_file_exists(resolved)

    def get_metadata(self) -> Dict[str, Any]:
        """Return minimal document metadata without heavy PDF dependencies."""
        return {
            "document_path": str(self.document_path),
            "document_name": self.document_path.name,
=======
    """Tracks procedural memory source document metadata."""

    DEFAULT_PDF_PATH = data_path("memory", "procedural_memory", "OJ_L_202401689_EN_TXT.pdf")

    def __init__(self, document_path: Path | None = None) -> None:
        self.document_path = ensure_file_exists(Path(document_path or self.DEFAULT_PDF_PATH))

    def get_metadata(self) -> dict:
        """Return minimal metadata without requiring heavy PDF dependencies."""
        return {
            "document_path": str(self.document_path),
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
            "document_size_bytes": self.document_path.stat().st_size,
        }
