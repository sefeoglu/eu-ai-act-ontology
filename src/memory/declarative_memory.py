"""Declarative memory: reusable ontology engineering knowledge."""

from pathlib import Path
from typing import Optional

from src.memory.memory import OntologyMemory
from src.utils import data_path, ensure_file_exists


class DeclarativeMemory(OntologyMemory):
    """Wraps a reference ontology for pattern reuse."""

    DEFAULT_PATH: Path = data_path("memory", "declarative_memory", "vair.owl")

    def load_default(self) -> "DeclarativeMemory":
        """Load the default ontology shipped in the repository."""
        self.load(ensure_file_exists(self.DEFAULT_PATH))
        return self

    def load_from_path(self, path: Optional[Path]) -> "DeclarativeMemory":
        """Load from a user-supplied path, or fall back to the default."""
        if path is not None:
            self.load(ensure_file_exists(Path(path)))
        else:
            self.load_default()
        return self
