"""Procedural memory: regulatory source-document metadata."""

from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import json
from ..utils import data_path, ensure_file_exists


class ProceduralMemory:
    """Tracks the procedural memory source document path and metadata."""

    DEFAULT_PATH: Path = data_path(
        "memory", "procedural", "ai_act_full_content.json"
    )
    DEFAULT_COMPETENCY_QUESTIONS_PATH: Path = data_path(
        "competency_questions", "competency_questions.json"
    )
    DEFAULT_CONCEPT_EXTRACTION_OUTPUT_PATH: Path = data_path(
        "concept_extraction", "concepts.json"
    )
    DEFAULT_MAPPING_OUTPUT_PATH: Path = data_path(
        "concept_mappings", "mappings.json"
    )
    DEFAULT_EXISTING_ONTOLOGIES = (
        data_path("memory", "declarative", "existing_ontologies", "dpv-owl.rdf"),
        data_path("memory", "declarative", "existing_ontologies", "vair.owl"),
        data_path("memory", "declarative", "existing_ontologies", "aio-full.owl"),
        data_path("memory", "declarative", "existing_ontologies", "airo.owl"),
    )

    def __init__(
        self,
        document_path: Optional[Path] = None,
        competency_questions_path: Optional[Path] = None,
        concept_extraction_output_path: Optional[Path] = None,
        existing_ontologies: Optional[Iterable[Path]] = None,
        mapping_output_path: Optional[Path] = None,
    ) -> None:
        resolved = Path(document_path) if document_path else self.DEFAULT_PATH
        self.document_path: Path = ensure_file_exists(resolved)
        self.competency_questions_path: Path = Path(
            competency_questions_path or self.DEFAULT_COMPETENCY_QUESTIONS_PATH
        )
        self.concept_extraction_output_path: Path = Path(
            concept_extraction_output_path or self.DEFAULT_CONCEPT_EXTRACTION_OUTPUT_PATH
        )
        self.existing_ontologies = [
            Path(path)
            for path in (existing_ontologies or self.DEFAULT_EXISTING_ONTOLOGIES)
        ]
        self.mapping_output_path: Path = Path(
            mapping_output_path or self.DEFAULT_MAPPING_OUTPUT_PATH
        )

    def get_metadata(self) -> Dict[str, Any]:
        """Return minimal document metadata without heavy PDF dependencies."""
        return {
            "competency_questions_path": str(self.competency_questions_path),
            "document_path": str(self.document_path),
            "document_name": self.document_path.name,
            "document_size_bytes": self.document_path.stat().st_size,
            "document_content": json.loads(self.document_path.read_text(encoding="utf-8")),
            "concept_extraction_output_path": str(self.concept_extraction_output_path),
            "existing_ontologies": [str(p) for p in self.existing_ontologies],
            "mapping_output_path": str(self.mapping_output_path)
        }
