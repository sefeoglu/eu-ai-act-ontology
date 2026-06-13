"""Procedural memory: regulatory source-document metadata."""

from pathlib import Path
from typing import Any, Dict, Optional
import json
from utils import data_path, ensure_file_exists


class ProceduralMemory:
    """Tracks the procedural memory source document path and metadata."""

    DEFAULT_PATH: Path = data_path(
        "memory", "procedural", "ai_act_full_content.json"
    )

    def __init__(self, document_path: Optional[Path] = None, competency_questions_path: Optional[Path] = None, concept_extraction_output_path: Optional[Path] = None, existing_ontologies: Optional[list] = None, mapping_output_path: Optional[Path] = None) -> None:
        resolved = Path(document_path) if document_path else self.DEFAULT_PATH
        self.document_path: Path = ensure_file_exists(resolved)
        self.competency_questions_path: Optional[Path] = Path(competency_questions_path) 
        self.concept_extraction_output_path: Optional[Path] = Path(concept_extraction_output_path)
        self.existing_ontologies: Optional[list] = existing_ontologies
        self.mapping_output_path: Optional[Path] = Path(mapping_output_path)

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
