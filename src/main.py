"""Entry point for the EU AI Act ontology prototype pipeline.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from client.client_access import PrototypeClient
PACKAGE_PARENT = '..'

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

PREFIX = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2]) + "/"
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EU AI Act ontology prototype pipeline"
    )
    parser.add_argument(
        "goals",
        nargs="*",
        default=['memory_generation', 'borrow_concept_extraction'],
        help=(
             "Pipeline goal: 'memory_generation' | 'generate_competency_questions' | 'extract_concepts' | 'map_to_existing_ontologies' | 'generate_ontology' | 'borrow_concept_extraction'"
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
        "--competency_questions",
         metavar="PATH",
         default="eu-ai-act-ontology/competency_questions/competency_questions.json",
         help="Path to save generated competency questions (default: eu-ai-act-ontology/competency_questions/competency_questions.json)",
    )
    parser.add_argument(
        "--concept_extraction_output",
        metavar="PATH",
        default="eu-ai-act-ontology/concept_extraction/concepts.json",
        help="Path to save extracted concepts (default: eu-ai-act-ontology/concept_extraction/concepts.json)",
    )
    parser.add_argument(
        "--existing_ontologies",
        nargs="*",
        default=['eu-ai-act-ontology/memory/declarative/existing_ontologies/dpv-owl.rdf','eu-ai-act-ontology/memory/declarative/existing_ontologies/vair.owl', 'eu-ai-act-ontology/memory/declarative/existing_ontologies/aio-full.owl', 'eu-ai-act-ontology/memory/declarative/existing_ontologies/airo.owl'],
    )
    parser.add_argument(
        "--mapping_output",
        metavar="PATH",
        default="eu-ai-act-ontology/concept_mappings/mappings_3.json",
        help="Path to save mapping results (default: eu-ai-act-ontology/concept_mappings/mappings_3.json)",
    )
    parser.add_argument(
        "--ontology_output",
        metavar="PATH",
        default="eu-ai-act-ontology/ontology/proof_of_concept_ontology_new_no_map.ttl",
        help="Path to save the generated ontology"
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        default="eu-ai-act-ontology/config/api_configs.json",
        help="Path to the API configuration file (default: eu-ai-act-ontology/config/api_configs.json)"
     )  
    
    return parser


def run_pipeline(
    goals: str,
    declarative_path: Optional[Path] = None,
    procedural_path: Optional[Path] = None,
    competency_questions_path: Optional[Path] = None,
    concept_extraction_output_path: Optional[Path] = None,
    existing_ontologies: Optional[List[Path]] = None,
    mapping_output_path: Optional[Path] = None,
    ontology_output_path: Optional[Path] = None,
    run_config_path: Optional[Path] = None

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
        run_config_path=run_config_path,
        ontology_output_path=ontology_output_path
    )
    return ui.run_pipeline(goals)


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    report = run_pipeline(
        goals=args.goals,
        declarative_path=PREFIX+args.declarative,
        procedural_path=PREFIX+args.procedural,
        competency_questions_path=PREFIX+args.competency_questions,
        concept_extraction_output_path=PREFIX+args.concept_extraction_output,
        existing_ontologies=[PREFIX+str(ont) for ont in args.existing_ontologies],
        mapping_output_path=PREFIX+args.mapping_output,
        ontology_output_path=PREFIX+args.ontology_output,
        run_config_path=PREFIX+args.config
    )
    print("Pipeline execution report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    print("Starting EU AI Act ontology prototype pipeline...")
    print(PREFIX)
    # main()
