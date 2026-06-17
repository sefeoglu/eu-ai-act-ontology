"""Procedural memory: regulatory source-document metadata."""

from pathlib import Path
from typing import Any, Dict, Optional
import json
from utils import data_path, ensure_file_exists
from host.agents.retriever_agent import retrieve_content

class ProceduralMemory:
    """Tracks the procedural memory source document path and metadata."""

    DEFAULT_PATH: Path = data_path(
        "memory", "procedural", "ai_act_full_content.json"
    )

    def __init__(self, document_path: Optional[Path] = None, competency_questions_path: Optional[Path] = None, concept_extraction_output_path: Optional[Path] = None, existing_ontologies: Optional[list] = None, mapping_output_path: Optional[Path] = None, config=None) -> None:
        resolved = Path(document_path) if document_path else self.DEFAULT_PATH
        self.document_path: Path = ensure_file_exists(resolved)
        self.competency_questions_path: Optional[Path] = Path(competency_questions_path) 
        self.concept_extraction_output_path: Optional[Path] = Path(concept_extraction_output_path)
        self.existing_ontologies: Optional[list] = existing_ontologies
        self.mapping_output_path: Optional[Path] = Path(mapping_output_path)

        self.content_retriever(config)

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
    def content_retriever(self, config_path=None) -> Dict[str, Any]:

        """Return the full content of the procedural memory document."""


        resolved_config_path = Path(config_path) if config_path else None
        config = json.loads(resolved_config_path.read_text(encoding="utf-8")) if resolved_config_path else {}
        url =  config['crawler']['base_url'] if 'crawler' in config and 'base_url' in config['crawler'] else None
        output = self.document_path
        timeout = config['crawler']['request_timeout'] if 'crawler' in config and 'request_timeout' in config['crawler'] else None
        user_agent = config['crawler']['headers']['User-Agent'] if 'crawler' in config and 'headers' in config['crawler'] and 'User-Agent' in config['crawler']['headers'] else None    
        if not all([url, output, timeout, user_agent]):
            raise ValueError("Missing crawler configuration parameters in config file.")
        if not self.document_path.exists():
            print(f"Document path {self.document_path} does not exist. Attempting to retrieve content from {url}...")
            retrieve_content(url=url, output=output, timeout=timeout, user_agent=user_agent)
        else:
            print(f"Document path {self.document_path} already exists. Skipping content retrieval.")


