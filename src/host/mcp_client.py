"""Tiny local MCP-style dispatcher for the prototype."""

from server.onto_generator_server import OntologyGenerator


class MCPClient:
    """Dispatches planned actions to ontology generator methods."""

    def __init__(self) -> None:
        self.generator = OntologyGenerator()

    def execute(self, action: str):
        if not hasattr(self.generator, action):
            raise ValueError(f"Unsupported action: {action}")
        return getattr(self.generator, action)()
