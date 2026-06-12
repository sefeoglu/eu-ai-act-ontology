"""Entry point for the EU AI Act ontology prototype pipeline.

Usage
-----
    python -m src.main [GOAL] [--declarative PATH] [--procedural PATH]

GOAL is one of:
    "memory_generation"  : generate declarative and procedural memory from the PDF (default)
    "generate competency questions" : create competency questions from the procedural text
    "list concepts"      : extract labeled ontology concepts (default)
    "show mappings"      : top namespace occurrence counts
    "generate ontology"  : create a new OWL/RDF ontology from the procedural memory
    "validate ontology"  : structural health check
    "show queries"       : SPARQL query catalog
    "export package"     : packaging metadata

Memory files can be overridden via --declarative / --procedural; the
bundled repository assets are used when not specified.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.client.ui import PrototypeUI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EU AI Act ontology prototype pipeline"
    )
    parser.add_argument(
        "goals",
        nargs="*",
        default=['memory_generation', 'generate_competency_questions', 'list_concepts', 'show_mappings', 'validate_ontology', 'show_queries', 'export_package' ],
        help=(
             "Pipeline goal: 'memory_generation' | 'generate_competency_questions' | 'list_concepts' | 'show_mappings' | 'generate_ontology' | 'validate_ontology' | "
            "'show_queries' | 'export_package'"
        ),
    )
    parser.add_argument(
        "--declarative",
        metavar="PATH",
        type=Path,
        default=None,
        help="Path to a declarative-memory OWL/RDF ontology file (optional).",
    )
    parser.add_argument(
        "--procedural",
        metavar="PATH",
        type=Path,
        default=None,
        help="Path to the procedural-memory regulatory PDF (optional).",
    )
    return parser


def run_pipeline(
    goals: str,
    declarative_path: Optional[Path] = None,
    procedural_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Instantiate the UI with the given memory files and run the pipeline."""
    ui = PrototypeUI(
        declarative_ontology_path=declarative_path,
        procedural_pdf_path=procedural_path,
    )
    return ui.run_pipeline(goals)


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    report = run_pipeline(
        goals=args.goals,
        declarative_path=args.declarative,
        procedural_path=args.procedural,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
