"""Prototype UI: loads memory files and drives the full pipeline."""

from pathlib import Path
from typing import Any, Dict, Optional

from src.host.llm_planner import LLMPlanner
from src.host.mcp_client import MCPClient
from src.host.validation_controller import ValidationController
from src.memory.memory_generator import MemoryGenerator
from src.server.onto_generator_server import OntologyGenerator


class PrototypeUI:
    """Orchestrates memory loading, planning, execution, and validation.

    Memory files are loaded here so that the caller (main.py or a test)
    can supply custom paths; the pipeline is fully initialised before any
    action is dispatched.

    Parameters
    ----------
    declarative_ontology_path:
        Path to an OWL/RDF ontology file.  Defaults to the bundled
        ``vair.owl`` when *None*.
    procedural_pdf_path:
        Path to the regulatory PDF document.  Defaults to the bundled
        EU AI Act PDF when *None*.
    config:
        Optional extra configuration forwarded to MemoryGenerator.
    """

    def __init__(
        self,
        declarative_ontology_path: Optional[Path] = None,
        procedural_pdf_path: Optional[Path] = None,
        config: Optional[Dict] = None,
    ) -> None:
        self._config = config or {}

        # 1. Build memory objects from the supplied (or default) file paths.
        generator = MemoryGenerator(self._config)
        self.declarative_memory = generator.generate_declarative_memory(
            ontology_path=declarative_ontology_path
        )
        self.procedural_memory = generator.generate_procedural_memory(
            document_path=procedural_pdf_path
        )

        # 2. Construct the pipeline components using the loaded memory.
        ontology_generator = OntologyGenerator(memory=self.declarative_memory)
        self.planner = LLMPlanner()
        self.client = MCPClient(generator=ontology_generator)
        self.validator = ValidationController()

    # ------------------------------------------------------------------
    # Pipeline entry point
    # ------------------------------------------------------------------

    def run_pipeline(self, goals: str) -> Dict[str, Any]:
        """Run the full pipeline for *goals* and return a structured report.

        Steps
        -----
        1. Plan: map the goals to a concrete action.
        2. Execute: dispatch the action via the MCP client.
        3. Validate: verify the result is non-empty.
        4. Return: assemble the full pipeline report.
        """
        # Step 1 – plan


        
        plan = self.planner.create_plan(goals)

        # Step 2 – execute
        result = self.client.execute(plan["action"])

        # Step 3 – validate
        if goals == "":
            validation = self.validator.validate_result(result)

        # Step 4 – report

        
        return {
            "goals": goals,
            "plan": plan,
            "memory": {
                "declarative_source": str(self.declarative_memory.source_path),
                "declarative_triples": self.declarative_memory.triple_count(),
                "procedural_source": self.procedural_memory.get_metadata(),
            },
            "validation": validation,
            "result": result,
        }
