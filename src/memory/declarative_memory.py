"""Declarative-memory access for reusable ontology knowledge."""

from pathlib import Path

from memory.memory import OntologyMemory
from utils import data_path, ensure_file_exists


class DeclarativeMemory(OntologyMemory):
    """Loads a reference ontology used for the prototype."""

    DEFAULT_PATH = data_path("memory", "declarative_memory", "vair.owl")

    def load_default(self) -> None:
        """Load the default ontology shipped in the repository."""
        self.load(ensure_file_exists(Path(self.DEFAULT_PATH)))
