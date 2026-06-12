"""Procedural memory: regulatory source-document metadata."""

from pathlib import Path
from typing import Any, Dict, Optional

from src.utils import data_path, ensure_file_exists


class ProceduralMemory:
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
            "document_size_bytes": self.document_path.stat().st_size,
        }
