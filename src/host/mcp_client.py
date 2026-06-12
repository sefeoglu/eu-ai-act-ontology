"""Local MCP-style dispatcher that executes pipeline actions."""

from typing import Any

from src.server.onto_generator_server import OntologyGenerator

ALLOWED_ACTIONS = frozenset({
    "extract_concepts",
    "validate_ontology",
    "map_to_existing_ontologies",
    "generate_sparql_queries",
    "generate_owl_ttl",
    "export_github_package",
})


class MCPClient:
    """Routes planned actions to the OntologyGenerator."""

    def __init__(self, generator: OntologyGenerator) -> None:
        self.generator = generator

    def execute(self, action: str) -> Any:
        """Dispatch *action* to the underlying generator."""
        if action not in ALLOWED_ACTIONS:
            raise ValueError(
                f"Unsupported action '{action}'. "
                f"Allowed: {sorted(ALLOWED_ACTIONS)}"
            )
        return getattr(self.generator, action)()
