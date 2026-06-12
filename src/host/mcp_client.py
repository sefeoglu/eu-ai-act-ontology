"""Tiny local MCP-style dispatcher for the prototype."""

from typing import Any

from src.server.onto_generator_server import OntologyGenerator


class MCPClient:
    """Dispatches planned actions to ontology generator methods."""

    ALLOWED_ACTIONS = {
        "extract_concepts",
        "validate_ontology",
        "map_to_existing_ontologies",
        "generate_sparql_queries",
        "generate_owl_ttl",
        "export_github_package",
    }

    def __init__(self) -> None:
        self.generator = OntologyGenerator()

    def execute(self, action: str) -> Any:
        if action not in self.ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported action: {action}")
        return getattr(self.generator, action)()
