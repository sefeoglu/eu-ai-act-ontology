<<<<<<< HEAD
"""Local MCP-style dispatcher that executes pipeline actions."""
=======
"""Tiny local MCP-style dispatcher for the prototype."""
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7

from typing import Any

from src.server.onto_generator_server import OntologyGenerator

<<<<<<< HEAD
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
=======

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
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
        return getattr(self.generator, action)()
