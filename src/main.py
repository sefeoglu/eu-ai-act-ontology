"""Entry point for the EU AI Act ontology prototype pipeline.
"""

import argparse
import copy
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
PACKAGE_PARENT = '..'

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve_path(value: Optional[Any]) -> Optional[str]:
    if value is None:
        return None

    path_str = str(value).strip()
    if not path_str:
        return None
    if os.path.isabs(path_str):
        return path_str

    path = Path(path_str)
    if path.parts and path.parts[0] == REPO_ROOT.name:
        path = Path(*path.parts[1:])
    return str(REPO_ROOT / path)


def _default_main_params() -> Dict[str, Any]:
    defaults = vars(build_cli_parser().parse_args([])).copy()
    defaults.pop("ui", None)
    return defaults


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EU AI Act ontology prototype pipeline"
    )
    parser.add_argument(
        "goals",
        nargs="*",
        default=['memory_generation', 'generate_chapter_based_ontology'],
        help=(
               "Pipeline goal: 'memory_generation' | 'generate_competency_questions' | 'extract_concepts' | 'generate_ontology' | 'generate_chapter_based_ontology' | 'map_to_existing_ontologies' | 'borrow_concept_extraction'"
        ),
    )
    parser.add_argument(
        "--declarative",
        default="eu-ai-act-ontology/memory/declarative/existing_ontologies/aio-full.owl",
        help="Path to a declarative-memory OWL/RDF ontology file.",
    )
    parser.add_argument(
        "--procedural",
        default="eu-ai-act-ontology/memory/procedural/ai_act_full_content.json",
        help="Path to the procedural-memory regulatory JSON file.",
    )
    parser.add_argument(
        "--competency_questions",
         metavar="PATH",
         type=Path,
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
        default="eu-ai-act-ontology/concept_mappings/mappings.json",
        help="Path to save mapping results (default: eu-ai-act-ontology/concept_mappings/mappings.json)",
    )
    parser.add_argument(
        "--ontology_output",
        metavar="PATH",
        default="eu-ai-act-ontology/ontology/proof_of_concept_ontology.ttl",
        help="Path to save the generated ontology"
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        default="eu-ai-act-ontology/config/api_configs.json",
        help="Path to the API configuration file (default: eu-ai-act-ontology/config/api_configs.json)"
     )
    parser.add_argument(
        "--concept_limit",
        type=int,
        default=500,
        help="Maximum number of extracted concept records to use for ontology generation (default: 500)",
    )
    parser.add_argument(
        "--chapter_limit",
        type=int,
        default=7,
        help="Maximum number of chapters to process during concept extraction (default: 7)",
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch a local web UI for configuring and running the pipeline.",
    )
    
    return parser


def run_prototype_pipeline(
    goals: str,
    declarative_path: Optional[Path] = None,
    procedural_path: Optional[Path] = None,
    competency_questions_path: Optional[Path] = None,
    concept_extraction_output_path: Optional[Path] = None,
    existing_ontologies: Optional[List[Path]] = None,
    mapping_output_path: Optional[Path] = None,
    ontology_output_path: Optional[Path] = None,
    run_config_path: Optional[Path] = None,
    concept_limit: int = 500,
    chapter_limit: int = 7,

) -> Dict[str, Any]:
    """Create the prototype client with the given inputs and run the pipeline."""
    from client.client_access import PrototypeClient

    prototype_client = PrototypeClient(
        declarative_ontology_path=declarative_path,
        procedural_pdf_path=procedural_path,
        config={
            "competency_questions_path": competency_questions_path,
            "concept_extraction_output_path": concept_extraction_output_path,
            "existing_ontologies": existing_ontologies,
            "mapping_output_path": mapping_output_path,
            "run_config_path": run_config_path,
        },
        run_config_path=run_config_path,
        ontology_output_path=ontology_output_path,
        concept_limit=concept_limit,
        chapter_limit=chapter_limit,
    )
    return prototype_client.run_pipeline(goals)


def main(
    argv: Optional[List[str]] = None,
    params: Optional[Dict[str, Any]] = None,
    print_report: bool = True,
) -> List[Dict[str, Any]]:
    if argv is not None and params is not None:
        raise ValueError("Pass either argv or params to main(), not both.")

    if params is None:
        args = build_cli_parser().parse_args(argv)
        if args.ui:
            from presentation.web_ui import launch_web_ui

            ui_defaults = _default_main_params()
            ui_defaults.update({"goals": list(args.goals)})
            launch_web_ui(ui_defaults)
            return []
        resolved_params: Dict[str, Any] = vars(args)
    else:
        resolved_params = _default_main_params()
        resolved_params.update(copy.deepcopy(params))

    report = run_prototype_pipeline(
        goals=resolved_params["goals"],
        declarative_path=_resolve_path(resolved_params["declarative"]),
        procedural_path=_resolve_path(resolved_params["procedural"]),
        competency_questions_path=_resolve_path(resolved_params["competency_questions"]),
        concept_extraction_output_path=_resolve_path(resolved_params["concept_extraction_output"]),
        existing_ontologies=[_resolve_path(ont) for ont in resolved_params["existing_ontologies"]],
        mapping_output_path=_resolve_path(resolved_params["mapping_output"]),
        ontology_output_path=_resolve_path(resolved_params["ontology_output"]),
        run_config_path=_resolve_path(resolved_params["config"]),
        concept_limit=resolved_params["concept_limit"],
        chapter_limit=resolved_params["chapter_limit"],
    )
    if print_report:
        print("Pipeline execution report:")
        print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    print("Starting EU AI Act ontology prototype pipeline...")
    print(str(REPO_ROOT.parent) + "/")
    main()
