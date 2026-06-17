"""Prototype UI: loads memory files and drives the full pipeline."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from host.llm_planner import LLMPlanner
from host.mcp_client import MCPClient
from memory.memory_generator import MemoryGenerator
from server.onto_generator_server import OntologyGenerator


class PrototypeClient:
    """Loads memory files, instantiates the pipeline components, and runs the full pipeline for given goals."""
    """Parameters
    ----------
    declarative_ontology_path: Optional[Path]
        Path to the declarative memory ontology file (e.g., TTL or RDF). If None, a default path will be used.
    procedural_pdf_path: Optional[Path]
        Path to the procedural memory PDF document. If None, a default path will be used.
    config: Optional[Dict]
        Configuration dictionary for the pipeline components (e.g., paths for intermediate outputs). If None, default values will be used.
    ontology_output_path: Optional[Path]
        Path to save the generated ontology. If None, a default path will be used.
    run_config_path: Optional[Path]
        Path to the run configuration file (e.g., API configs). If None, a default path will be used.
    """

    def __init__(
        self,
        declarative_ontology_path: Optional[Path] = None,
        procedural_pdf_path: Optional[Path] = None,
        config: Optional[Dict] = None,
        ontology_output_path: Optional[Path] = None,
        run_config_path: Optional[Path] = None,
        concept_limit: int = None,
        chapter_limit: int = None,
    ) -> None:
        
        """
        Args:
        declarative_ontology_path: Optional[Path]
            Path to the declarative memory ontology file (e.g., TTL or RDF). If None, a default path will be used.
        procedural_pdf_path: Optional[Path]
            Path to the procedural memory PDF document. If None, a default path will be used.
        config: Optional[Dict]
            Configuration dictionary for the pipeline components (e.g., paths for intermediate outputs). If None, default values will be used.
        ontology_output_path: Optional[Path]
            Path to save the generated ontology. If None, a default path will be used.
        run_config_path: Optional[Path]
            Path to the run configuration file (e.g., API configs). If None, a default path will be used.
        """

        self._config = config or {}
        self._ontology_output_path = ontology_output_path
        self._run_config_path = run_config_path
        if concept_limit is None or chapter_limit is None:
            raise ValueError("concept_limit and chapter_limit must be provided from the caller")
        self._concept_limit = concept_limit
        self._chapter_limit = chapter_limit

        memory_generator = MemoryGenerator(self._config)
        self.declarative_memory = memory_generator.generate_declarative_memory(
            ontology_path=declarative_ontology_path
        )
        self.procedural_memory = memory_generator.generate_procedural_memory(
            document_path=procedural_pdf_path
        )

        ontology_generator = OntologyGenerator(
            declarative_memory=self.declarative_memory,
            procedural_memory=self.procedural_memory,
            output_path=self._ontology_output_path,
            run_config_path=self._run_config_path,
            concept_limit=self._concept_limit,
            chapter_limit=self._chapter_limit,
        )
        self.planner = LLMPlanner()
        self.client = MCPClient(generator=ontology_generator)

    # ------------------------------------------------------------------
    # Pipeline entry point
    # ------------------------------------------------------------------

    def run_pipeline(self, goals: List[str]) -> List[Dict[str, Any]]:
        """Run the full pipeline for *goals* and return a structured report.

        Steps
        -----
        1. Plan: map the goals to a concrete action.
        2. Execute: dispatch the action via the MCP client.
        3. Return: assemble the full pipeline report.
        """
        """Parameters
        ----------
        goals: List[str]
            A list of pipeline goals to execute.

        Returns
        -------
        List[Dict[str, Any]]
            A structured report per goal containing the plan, memory context,
            and execution result.
        """
        reports = []

        for goal in goals:
            print(f"Processing goal: {goal}")
            plan = self.planner.create_plan(goal)
            result = self.client.execute(plan["action"])

            goal_report = {
                "goal": goal,
                "plan": plan,
                "memory": {
                    "declarative_source": str(self.declarative_memory.source_path),
                    "declarative_triples": self.declarative_memory.triple_count(),
                    "procedural_source": self.procedural_memory.get_metadata(),
                },
                "result": result,
            }
            reports.append(goal_report)

        return reports