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

""" This module defines the MCPClient class, which serves as a local dispatcher for executing planned actions related to ontology generation. The MCPClient routes specific action requests to the corresponding methods of the OntologyGenerator, allowing for a modular and extensible architecture. Each action corresponds to a distinct step in the ontology generation pipeline, such as memory generation, competency question generation, concept extraction, mapping to existing ontologies, and the final ontology generation. By centralizing the execution logic within the MCPClient, we can maintain a clear separation of concerns between planning and execution, facilitating easier maintenance and potential future enhancements to the pipeline.
"""
class MCPClient:
    """Routes planned actions to the OntologyGenerator."""

    def __init__(self, generator: OntologyGenerator) -> None:
        self.generator = generator

    def execute(self, action: str) -> Any:
        """Dispatch *action* to the underlying generator."""
        """Args:
        action: str
            The name of the action to execute, which should correspond to a method in the OntologyGenerator (e.g., 'memory_generation', 'generate_competency_questions').
        Returns:
        Any
            The result of the executed action.
        Raises:
        ValueError
            If the action is not supported.
        """

        print(f"Executing action: {action}")
        if action not in ALLOWED_ACTIONS:
            raise ValueError(
                f"Unsupported action '{action}'. "
                f"Allowed: {sorted(ALLOWED_ACTIONS)}"
            )
        return getattr(self.generator, action)()
