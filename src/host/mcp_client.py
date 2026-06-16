"""Local MCP-style dispatcher that executes pipeline actions."""

from typing import Any

from server.onto_generator_server import OntologyGenerator

ALLOWED_ACTIONS = frozenset({
    "memory_generation",
    "generate_competency_questions",
    "extract_concepts",
    "map_to_existing_ontologies",
    "generate_ontology",
    "borrow_concept_extraction"
})


class MCPClient:
    """Routes planned actions to the OntologyGenerator."""

    def __init__(self, generator: OntologyGenerator) -> None:
        self.generator = generator

    def execute(self, action: str) -> Any:
        """Dispatch *action* to the underlying generator."""
        print(f"Executing action: {action}")
        if action not in ALLOWED_ACTIONS:
            raise ValueError(
                f"Unsupported action '{action}'. "
                f"Allowed: {sorted(ALLOWED_ACTIONS)}"
            )
        return getattr(self.generator, action)()
