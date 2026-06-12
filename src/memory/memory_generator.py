"""Build declarative and procedural memory objects from configuration."""

import code
from email.mime import text
from pathlib import Path
from typing import Dict, List, Optional

from src.memory.declarative_memory import DeclarativeMemory
from src.memory.procedural_memory import ProceduralMemory
from host.agents.ocr_agent import ocr_pdf
from logging import getLogger
logger = getLogger(__name__)

class MemoryGenerator:
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
        text = self.pdf_to_text(text) if text.endswith(".pdf") else text
        return self.split_text_into_chunks(text=text, chunk_size=chunk_size)
    


    def split_pdf_into_pages(self, pdf_path: str, output_folder_path:str) -> List[str]:
        """Split a PDF into individual pages."""
        """include code"""
        return text

    def pdf_to_text(self, pdf_path: str) -> str:
        """Extract text from a PDF file (placeholder implementation)."""
        logger.info(f"Extracting text from PDF: {pdf_path}")
        text = ocr_pdf(pdf_path, self.config.get("ocr_model_config", {}))
        logger.info(f"Extracted text from PDF: {pdf_path}")
        return text
