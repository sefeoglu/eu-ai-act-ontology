"""Entry point for the EU AI Act ontology prototype."""

import argparse
import json

from src.client.ui import PrototypeUI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EU AI Act ontology prototype")
    parser.add_argument(
        "goal",
        nargs="?",
        default="list concepts",
        help="Prototype goal (e.g. 'list concepts', 'validate ontology', 'show mappings').",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ui = PrototypeUI()
    output = ui.run_goal(args.goal)
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
