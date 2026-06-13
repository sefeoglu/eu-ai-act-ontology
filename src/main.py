"""Entry point for the EU AI Act ontology prototype pipeline.

Usage
-----
    python -m src.main [GOAL] [--declarative PATH] [--procedural PATH]

Memory files can be overridden via --declarative / --procedural; the bundled repository assets are used when not specified.
"""

import argparse

from pathlib import Path
from typing import Any, Dict, List, Optional

from .client.client_access import PrototypeClient
from .memory.procedural_memory import ProceduralMemory
from .utils import data_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EU AI Act ontology prototype pipeline"
    )
    parser.add_argument(
        "goals",
        nargs="*",
        default=['memory_generation', 'generate_competency_questions', 'extract_concepts', 'map_to_existing_ontologies', 'generate_ontology'],
        help=(
             "Pipeline goal: 'memory_generation' | 'generate_competency_questions' | 'extract_concepts' | 'map_to_existing_ontologies' | 'generate_ontology'"
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
    parser.add_argument(
        "--comptency_questions",
         "--competency_questions",
         metavar="PATH",
         dest="competency_questions",
         type=Path,
         default=ProceduralMemory.DEFAULT_COMPETENCY_QUESTIONS_PATH,
         help="Path to save generated competency questions.",
    )
    parser.add_argument(
        "--concept_extraction_output",
        metavar="PATH",
        type=Path,
        default=ProceduralMemory.DEFAULT_CONCEPT_EXTRACTION_OUTPUT_PATH,
        help="Path to save extracted concepts.",
    )
    parser.add_argument(
        "--existing_ontologies",
        nargs="*",
        type=Path,
        default=list(ProceduralMemory.DEFAULT_EXISTING_ONTOLOGIES),
    )
    parser.add_argument(
        "--mapping_output",
        metavar="PATH",
        type=Path,
        default=ProceduralMemory.DEFAULT_MAPPING_OUTPUT_PATH,
        help="Path to save mapping results.",
    )
    parser.add_argument(
        "--ontology_output",
        metavar="PATH",
        type=Path,
        default=data_path("ontology", "proof_of_concept_ontology.ttl"),
        help="Path to save the generated ontology"
    )
    
    return parser


def run_pipeline(
    goals: List[str],
    declarative_path: Optional[Path] = None,
    procedural_path: Optional[Path] = None,
    competency_questions_path: Optional[Path] = None,
    concept_extraction_output_path: Optional[Path] = None,
    existing_ontologies: Optional[List[Path]] = None,
    mapping_output_path: Optional[Path] = None,
    ontology_output_path: Optional[Path] = None,

) -> Dict[str, Any]:
    """Instantiate the UI with the given memory files and run the pipeline."""
    ui = PrototypeClient(
        declarative_ontology_path=declarative_path,
        procedural_pdf_path=procedural_path,
        config={
            "competency_questions_path": competency_questions_path,
            "concept_extraction_output_path": concept_extraction_output_path,
            "existing_ontologies": existing_ontologies,
            "mapping_output_path": mapping_output_path,
        },
        ontology_output_path=ontology_output_path
    )
    return ui.run_pipeline(goals)


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    report = run_pipeline(
        goals=args.goals,
        declarative_path=args.declarative,
        procedural_path=args.procedural,
        competency_questions_path=args.competency_questions,
        concept_extraction_output_path=args.concept_extraction_output,
        existing_ontologies=args.existing_ontologies,
        mapping_output_path=args.mapping_output,
        ontology_output_path=args.ontology_output,
        
    )
    # print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
