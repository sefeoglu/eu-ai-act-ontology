"""Declarative memory: reusable ontology engineering knowledge."""

from pathlib import Path
from typing import Optional

from .onto_memory import OntologyMemory
from ..utils import data_path, ensure_file_exists


class DeclarativeMemory(OntologyMemory):
    """Wraps a reference ontology for pattern reuse."""

    DEFAULT_PATH: Path = data_path(
        "memory",
        "declarative",
        "existing_ontologies",
        "vair.owl",
    )

    def load_default(self) -> "DeclarativeMemory":
        """Load the default ontology shipped in the repository."""
        self.load(ensure_file_exists(self.DEFAULT_PATH))
        return self

    def load_from_path(self, path: Optional[Path]) -> "DeclarativeMemory":
        """Load from a user-supplied path, or fall back to the default."""
        ontology_path = ensure_file_exists(Path(path)) if path is not None else self.DEFAULT_PATH
        self.load(ontology_path)
        return self