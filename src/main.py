<<<<<<< HEAD
"""Entry point for the EU AI Act ontology prototype pipeline.

Usage
-----
    python -m src.main [GOAL] [--declarative PATH] [--procedural PATH]

GOAL is one of:
    "list concepts"      – extract labeled ontology concepts (default)
    "validate ontology"  – structural health check
    "show mappings"      – top namespace occurrence counts
    "show queries"       – SPARQL query catalog
    "export package"     – packaging metadata

Memory files can be overridden via --declarative / --procedural; the
bundled repository assets are used when not specified.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
=======
"""Entry point for the EU AI Act ontology prototype."""

import argparse
import json
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7

from src.client.ui import PrototypeUI


def build_parser() -> argparse.ArgumentParser:
<<<<<<< HEAD
    parser = argparse.ArgumentParser(
        description="EU AI Act ontology prototype pipeline"
    )
=======
    parser = argparse.ArgumentParser(description="EU AI Act ontology prototype")
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
    parser.add_argument(
        "goal",
        nargs="?",
        default="list concepts",
<<<<<<< HEAD
        help=(
            "Pipeline goal: 'list concepts' | 'validate ontology' | "
            "'show mappings' | 'show queries' | 'export package'"
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
=======
        help="Prototype goal (e.g. 'list concepts', 'validate ontology', 'show mappings').",
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
    )
    return parser


<<<<<<< HEAD
def run_pipeline(
    goal: str,
    declarative_path: Optional[Path] = None,
    procedural_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Instantiate the UI with the given memory files and run the pipeline."""
    ui = PrototypeUI(
        declarative_ontology_path=declarative_path,
        procedural_pdf_path=procedural_path,
    )
    return ui.run_pipeline(goal)


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    report = run_pipeline(
        goal=args.goal,
        declarative_path=args.declarative,
        procedural_path=args.procedural,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
=======
def main() -> None:
    args = build_parser().parse_args()
    ui = PrototypeUI()
    output = ui.run_goal(args.goal)
    print(json.dumps(output, indent=2, ensure_ascii=False))
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7


if __name__ == "__main__":
    main()
