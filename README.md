# Memory-Assisted Ontology Engineering Architecture for Regulatory Knowledge
![Python](https://img.shields.io/badge/Python-3.10+-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Ontology](https://img.shields.io/badge/ontology-Turtle-7E57C2)
![Architecture](https://img.shields.io/badge/Architecture-Memory--assisted%20MCP-0F766E)
![Agents](https://img.shields.io/badge/Agents-Domain%20expert%20%26%20retriever-7C3AED)
![Domain](https://img.shields.io/badge/Domain-EU%20AI%20Act-9A3412)
![Validation](https://img.shields.io/badge/Validation-SPARQL-1D4ED8)
![Artifacts](https://img.shields.io/badge/Artifacts-Included-4D7C0F)

*This branch contains ongoing research extensions and improvements beyond the original task submission. The submitted version remains preserved in the release and master branch for reproducibility and evaluation purposes.*
## Project architecture

![Project architecture](figures/project_architecture.svg)

Source diagram: [figures/project_architecture.md](figures/project_architecture.md)

This repository contains a proof-of-concept pipeline for building an ontology from the EU AI Act with a memory-based MCP architecture. The project combines:

- **declarative memory** from reusable ontologies and prompt templates
- **procedural memory** from EU AI Act source material
- **LLM-driven orchestration** for competency question generation, concept extraction, ontology generation, and ontology reuse
- **dual entry surfaces** through the CLI and a local browser UI for configuring and monitoring runs

The repository also includes generated artifacts, evaluation material, simple validation scripts for the resulting ontology, and an architecture diagram that mirrors the current runtime flow.

**Note**: Copilot was used to refine README.md. It is not used for coding.

## Repository layout

```text
eu-ai-act-ontology/
├── competency_questions/             # Generated competency questions as JSON
├── concept_extraction/               # Extracted concepts as JSON
├── concept_mappings/                 # Mappings to reused ontologies
├── config/                           # Model and runtime configuration
├── doc/                              # Supporting project documentation
├── evaluated_competency_questions/   # Example SPARQL evaluation material
├── figures/                          # Figures used by the project
├── memory/
│   ├── declarative/
│   │   ├── existing_ontologies/      # Reused ontologies (DPV, VAIR, AIRO, AIO)
│   │   └── prompts/                  # Prompt templates for each pipeline stage
│   └── procedural/                   # Extracted EU AI Act source content (ai_act_full_content.json)
├── metrics/                          # Ontology structural metrics script and CSV outputs
├── ontology/                         # Generated proof-of-concept ontologies
├── src/
│   ├── client/                       # Pipeline entry client
│   ├── host/                         # Planning, dispatch, and validation components
│   ├── memory/                       # Declarative/procedural memory loaders
│   ├── presentation/                 # Local web UI for configuring and monitoring runs
│   ├── server/                       # Ontology generation logic
│   ├── main.py                       # Prototype pipeline entry module
│   └── utils.py                      # Shared helpers
└── test/                             # SPARQL-based validation script
```

## What the pipeline does

The accompanying documentation in [`doc/document.md`](doc/document.md) and
[`doc/proof_of_concept_eu-ai_act_ontology_documentation.pdf`](doc/proof_of_concept_eu-ai_act_ontology_documentation.pdf)
describes the broader seven-step ontology-development process that this
prototype supports. Within the repository, the automated workflow focuses on
these execution goals:

1. Generate competency questions from EU AI Act content
2. Extract ontology concepts from the generated questions
3. Generate an ontology in Turtle
4. Map generated classes and properties to existing ontologies
5. Borrow aligned concepts back into the generated ontology

The main orchestration code lives in:

- `src/main.py`
- `src/client/client_access.py`
- `src/server/onto_generator_server.py`

The local browser UI lives in:

- `src/presentation/web_ui.py`

At runtime, both the CLI and the local UI enter through `src/main.py`, which constructs the `PrototypeClient`. The client loads declarative and procedural memory, uses the `LLMPlanner` to map goals to actions, dispatches those actions through the `MCPClient`, and executes ontology tasks through the `OntologyGenerator`.

## Key inputs

- Declarative ontologies in `memory/declarative/existing_ontologies/`
- Prompt templates in `memory/declarative/prompts/`
- Procedural source content in `memory/procedural/ai_act_full_content.json`
- Runtime configuration in `config/api_configs.json`

`config/api_configs.json` contains placeholder API credentials and model settings. Replace the placeholder key values before running any LLM-backed steps.

## Installation

The package requires Python 3.10 or newer.

Create and activate a virtual environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

If you only want the raw dependencies without installing the package entry point, use:

```bash
python -m pip install -r requirements.txt
```

Before running any LLM-backed step, update the placeholder values in `config/api_configs.json`.

## Run as a package

After installation, you can run the pipeline through the console script:

```bash
eu-ai-act-ontology
```

The default run executes:

- `memory_generation`
- `generate_chapter_based_ontology`

To run specific pipeline goals explicitly:

```bash
eu-ai-act-ontology generate_competency_questions extract_concepts generate_ontology
```

You can also override the ontology-generation limits from the CLI:

```bash
eu-ai-act-ontology --concept_limit 250 --chapter_limit 5
```

## Run Web UI

If you want a browser-based control surface instead of passing every option on the command line, launch the built-in local UI:

```bash
eu-ai-act-ontology --ui
```

You can launch the same interface directly from the source tree if you prefer:

```bash
python src/main.py --ui
```

What the UI provides:

- goal selection for each pipeline stage
- editable repository-relative input and output paths
- configurable concept and chapter limits
- live progress updates, activity log entries, and the final structured report
- a stop control for ending the current background run

The UI is rendered directly by `src/presentation/web_ui.py` and does not require a separate frontend build step.

Operational notes:

- The UI binds to `127.0.0.1` on an ephemeral local port and opens in your default browser automatically.
- Keep the terminal process running while the UI is open.
- LLM-backed stages still require valid credentials in `config/api_configs.json`.

To see all available options:

```bash
eu-ai-act-ontology --help
```

You can also call the package programmatically. The `params` dictionary mirrors the full CLI argument set:

```python
from pathlib import Path

from main import main

root = Path.cwd()

report = main(
    params={
        "goals": ["memory_generation"],
        "declarative": root / "memory/declarative/existing_ontologies/aio-full.owl",
        "procedural": root / "memory/procedural/ai_act_full_content.json",
        "competency_questions": root / "competency_questions/competency_questions.json",
        "concept_extraction_output": root / "concept_extraction/concepts.json",
        "existing_ontologies": [
            root / "memory/declarative/existing_ontologies/dpv-owl.rdf",
            root / "memory/declarative/existing_ontologies/vair.owl",
            root / "memory/declarative/existing_ontologies/aio-full.owl",
            root / "memory/declarative/existing_ontologies/airo.owl",
        ],
        "mapping_output": root / "concept_mappings/mappings.json",
        "ontology_output": root / "ontology/proof_of_concept_ontology.ttl",
        "config": root / "config/api_configs.json",
        "concept_limit": 1,
        "chapter_limit": 1,
    },
    print_report=False,
)
```

## Generated artifacts

The repository already includes example outputs from the workflow:

- `competency_questions/competency_questions.json`
- `concept_extraction/concepts.json`
- `concept_mappings/mappings.json`
- `ontology/proof_of_concept_ontology_v0.1.ttl`
- `ontology/proof_of_concept_ontology_v0.2.ttl`
- `metrics/domain_ontology_structural_metrics_before_mapping.csv`
- `metrics/domain_ontology_structural_metrics_after_mapping.csv`

## Validation and evaluation

Final ontology for assessment: `ontology/proof_of_concept_ontology_v0.2.ttl`

Refined variant: `ontology/proof_of_concept_ontology_v0.3.ttl`

### Run the SPARQL validation script

```bash
python test/test_sparql.py
```

This script loads `ontology/proof_of_concept_ontology_v0.2.ttl` and executes example SPARQL queries for:

- high-risk AI systems
- provider compliance, documentation, and risk relations
- transparency obligations


### Compute structural metrics

```bash
python metrics/basic_metrics.py --input_file ontology/proof_of_concept_ontology_v0.2.ttl -f turtle -o metrics/domain_ontology_structural_metrics_after_mapping.csv
```

## Notes

- The repository is a prototype and includes generated outputs alongside source code.
- The top-level test script is an executable validation helper rather than a `unittest.TestCase` suite.
- Supporting documentation is available in both Markdown and PDF form under `doc/`.
- The refined ontology is available at `ontology/proof_of_concept_ontology_v0.3.ttl`.
- The architecture sources live in `figures/project_architecture.md` and `figures/project_architecture.mmd`, with the rendered asset committed as `figures/project_architecture.svg`.

## License

MIT
