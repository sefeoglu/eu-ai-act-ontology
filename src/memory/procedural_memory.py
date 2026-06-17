"""Procedural memory: regulatory source-document metadata."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from host.agents.retriever_agent import retrieve_and_save_ai_act_content
from utils import data_path, ensure_file_exists

class ProceduralMemory:
    """Tracks the procedural memory source document path and metadata."""

    DEFAULT_PATH: Path = data_path(
        "memory", "procedural", "ai_act_full_content.json"
    )

    def __init__(
        self,
        document_path: Optional[Path] = None,
        competency_questions_path: Optional[Path] = None,
        concept_extraction_output_path: Optional[Path] = None,
        existing_ontologies: Optional[List[Union[str, Path]]] = None,
        mapping_output_path: Optional[Path] = None,
        config: Optional[Union[str, Path]] = None,
    ) -> None:
        resolved = Path(document_path) if document_path else self.DEFAULT_PATH
        self.document_path: Path = ensure_file_exists(resolved)
        self.competency_questions_path: Optional[Path] = (
            Path(competency_questions_path) if competency_questions_path else None
        )
        self.concept_extraction_output_path: Optional[Path] = (
            Path(concept_extraction_output_path) if concept_extraction_output_path else None
        )
        self.existing_ontologies: List[str] = (
            [str(path) for path in existing_ontologies] if existing_ontologies else []
        )
        self.mapping_output_path: Optional[Path] = (
            Path(mapping_output_path) if mapping_output_path else None
        )

        self.ensure_document_content_available(config)

    def get_metadata(self) -> Dict[str, Any]:
        """Return minimal document metadata without heavy PDF dependencies."""
        return {
            "competency_questions_path": str(self.competency_questions_path),
            "document_path": str(self.document_path),
            "document_name": self.document_path.name,
            "document_size_bytes": self.document_path.stat().st_size,
            "document_content": json.loads(self.document_path.read_text(encoding="utf-8")),
            "concept_extraction_output_path": str(self.concept_extraction_output_path),
            "existing_ontologies": self.existing_ontologies,
            "mapping_output_path": str(self.mapping_output_path)
        }

    def ensure_document_content_available(
        self,
        config_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:

        """Return the full content of the procedural memory document."""


        resolved_config_path = Path(config_path) if config_path else None
        config = (
            json.loads(resolved_config_path.read_text(encoding="utf-8"))
            if resolved_config_path
            else {}
        )
        crawler_config = config.get("crawler", {})
        headers = crawler_config.get("headers", {})
        source_url = crawler_config.get("base_url")
        output_path = self.document_path
        request_timeout = crawler_config.get("request_timeout")
        user_agent = headers.get("User-Agent")

        if not all([source_url, output_path, request_timeout, user_agent]):
            raise ValueError("Missing crawler configuration parameters in config file.")

        if not self.document_path.exists():
            print(f"Document path {self.document_path} does not exist. Attempting to retrieve content from {source_url}...")
            retrieve_and_save_ai_act_content(
                url=source_url,
                output=output_path,
                timeout=request_timeout,
                user_agent=user_agent,
            )
        else:
            print(f"Document path {self.document_path} already exists. Skipping content retrieval.")

        return json.loads(self.document_path.read_text(encoding="utf-8"))


