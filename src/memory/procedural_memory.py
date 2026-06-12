"""Procedural memory helpers for regulatory source artifacts."""

from pathlib import Path

from src.utils import data_path, ensure_file_exists


class ProceduralMemory:
    """Tracks procedural memory source document metadata."""

    DEFAULT_PDF_PATH = data_path("memory", "procedural_memory", "OJ_L_202401689_EN_TXT.pdf")

    def __init__(self, document_path: Path | None = None) -> None:
        self.document_path = ensure_file_exists(Path(document_path or self.DEFAULT_PDF_PATH))

    def get_metadata(self) -> dict:
        """Return minimal metadata without requiring heavy PDF dependencies."""
        return {
            "document_path": str(self.document_path),
            "document_size_bytes": self.document_path.stat().st_size,
        }
