"""Build declarative and procedural memory objects from configuration."""

from pathlib import Path
from typing import Dict, Optional

from memory.declarative_memory import DeclarativeMemory
from memory.procedural_memory import ProceduralMemory
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
        print(f"Generating procedural memory with document path: {document_path}")
        path = document_path
        output_competency_questions_path = self.config.get("competency_questions_path")
        output_concept_extraction_path = self.config.get("concept_extraction_output_path")
        existing_ontologies = self.config.get("existing_ontologies")
        mapping_output_path = self.config.get("mapping_output_path")
        config_path = self.config.get("run_config_path")
        print(f"existing_ontologies: {existing_ontologies}")

        return ProceduralMemory(
            document_path=Path(path) if path else None,
            competency_questions_path=Path(output_competency_questions_path) if output_competency_questions_path else None,
            concept_extraction_output_path=Path(output_concept_extraction_path) if output_concept_extraction_path else None,

            existing_ontologies=[str(p) for p in existing_ontologies] if existing_ontologies else None,
            mapping_output_path=Path(mapping_output_path) if mapping_output_path else None,
            config=Path(config_path) if config_path else None
        )

