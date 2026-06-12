<<<<<<< HEAD
"""Build declarative and procedural memory objects from configuration."""

from pathlib import Path
from typing import Dict, List, Optional
=======
"""Generate procedural and declarative memory for the prototype agent."""
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7

from src.memory.declarative_memory import DeclarativeMemory
from src.memory.procedural_memory import ProceduralMemory


class MemoryGenerator:
<<<<<<< HEAD
    """Assembles the full memory context required by the prototype pipeline."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config: Dict = config or {}

    # ------------------------------------------------------------------
    # Declarative memory
    # ------------------------------------------------------------------

    def generate_declarative_memory(
        self, ontology_path: Optional[Path] = None
    ) -> DeclarativeMemory:
        """Load declarative memory from a path or repository defaults."""
        path = ontology_path or self.config.get("declarative_ontology")
        memory = DeclarativeMemory()
        memory.load_from_path(Path(path) if path else None)
        return memory

    # ------------------------------------------------------------------
    # Procedural memory
    # ------------------------------------------------------------------

    def generate_procedural_memory(
        self, document_path: Optional[Path] = None
    ) -> ProceduralMemory:
        """Load procedural memory from a path or repository defaults."""
        path = document_path or self.config.get("procedural_pdf")
        return ProceduralMemory(Path(path) if path else None)

    # ------------------------------------------------------------------
    # Text chunking helpers (used for future LLM prompt construction)
    # ------------------------------------------------------------------

    def split_text_into_chunks(
        self, text: str, chunk_size: int = 1_000
    ) -> List[str]:
        """Split extracted text into fixed-size character chunks.

        The default chunk size of 1 000 characters is suitable for
        passing regulatory-text passages to an LLM prompt window.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    def split_pdf_into_chunks(
        self, text: str, chunk_size: int = 1_000
    ) -> List[str]:
        """Backward-compatible alias that expects already-extracted PDF text."""
        return self.split_text_into_chunks(text=text, chunk_size=chunk_size)
=======
    """Build declarative/procedural memory objects from repository assets."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def generate_procedural_memory(self) -> dict:
        """Generate procedural memory metadata for the prototype."""
        procedural_memory = ProceduralMemory(self.config.get("procedural_pdf"))
        return procedural_memory.get_metadata()

    def split_text_into_chunks(self, text: str, chunk_size: int = 1_000) -> list[str]:
        """Split extracted text into fixed-size chunks (1000 chars by default) for LLM prompts."""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        return [text[index:index + chunk_size] for index in range(0, len(text), chunk_size)]

    def split_pdf_into_chunks(self, text: str, chunk_size: int = 1_000) -> list[str]:
        """Backward-compatible alias that expects already extracted PDF text."""
        return self.split_text_into_chunks(text=text, chunk_size=chunk_size)

    def generate_declarative_memory(self) -> DeclarativeMemory:
        """Load declarative memory based on configuration or defaults."""
        memory = DeclarativeMemory()
        ontology_path = self.config.get("declarative_ontology")
        if ontology_path:
            memory.load(ontology_path)
        else:
            memory.load_default()
        return memory
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
