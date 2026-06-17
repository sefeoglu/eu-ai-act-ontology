# Automated Ontology Development Using a Memory-Based MCP Approach
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Status](https://img.shields.io/badge/status-proof--of--concept-orange)
![Ontology](https://img.shields.io/badge/ontology-Turtle-7E57C2)


## TODOs for v0.2
- Distributed ontology generation based on chapters.
- Merge local ontologies and generate a global ontology.
- This distributed arch. will resolve the context window limitation of LLMs as well.


This repository contains a proof-of-concept pipeline for building an ontology from the EU AI Act with a memory-based MCP architecture. The project combines:

- **declarative memory** from reusable ontologies and prompt templates
- **procedural memory** from EU AI Act source material
- **LLM-driven orchestration** for competency question generation, concept extraction, ontology generation, and ontology reuse

The repository also includes generated artifacts, evaluation material, and simple validation scripts for the resulting ontology.

**Note**: Copilot was used to refine README.md. It is not used for coding.
## Repository layout

```text
eu-ai-act-ontology/
├── competency_questions/             # Generated competency questions as JSON
├── concept_extraction/               # Extracted concepts as JSON
├── concept_mappings/                 # Mappings to reused ontologies
├── config/                           # Model and crawler configuration
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

## Key inputs

- Declarative ontologies in `memory/declarative/existing_ontologies/`
- Prompt templates in `memory/declarative/prompts/`
- Procedural source content in `memory/procedural/ai_act_full_content.json`
- Runtime configuration in `config/api_configs.json`

`config/api_configs.json` contains placeholder API credentials and model settings. Replace the placeholder key values before running any LLM-backed steps.

## Installation

Install the Python dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
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

## License

MIT
