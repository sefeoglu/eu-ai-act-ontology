# Automated Ontology Development Using a Memory-Based MCP Approach

A memory-based MCP architecture for end-to-end ontology development, where LLM agents use declarative memory, procedural memory, and task-specific intermediate artefacts to support the full ontology engineering workflow: competency question generation, concept extraction, ontology reuse/mapping, and proof-of-concept ontology construction.


## Repository Structure

```xml
eu-ai-act-ontology/
├── competency_questions/       # Generated competency question artefacts
├── concept_extraction/         # Extracted concept outputs
├── concept_mappings/           # Ontology mapping outputs
├── config/                     # Runtime configuration files
├── doc/                        # Project documentation
├── evaluated_competency_questions/ # Evaluated CQ and SPARQL notes
├── figures/                    # Images used in documentation
├── memory/                     # Bundled memory assets
│   ├── declarative/            # Reusable ontologies and prompt assets
│   │   ├── existing_ontologies/
│   │   └── prompts/
│   └── procedural/             # Regulatory source memory
├── metrics/                    # Analysis scripts and exported metrics
├── ontology/                   # Generated ontology versions
├── src/
│   ├── client/                 # Client entry points for the pipeline
│   ├── host/                   # Planning, validation, and agent orchestration
│   │   └── agents/             # Agent implementations used by the host
│   ├── memory/                 # Memory loading and generation logic
│   ├── server/                 # Ontology generation services
│   ├── main.py                 # Main application entry point
│   └── utils.py                # Shared utilities
├── test/                       # Unit tests
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview
```

## Architecture

The system utilizes two complementary memory types:

### 1. Declarative Memory

Declarative memory stores ontology engineering knowledge derived from previously developed ontologies, including:

* Class and property modeling rules
* Domain and range constraints
* Reusable ontology structures

This memory enables the system to reuse established ontology modeling practices and maintain consistency across generated ontologies.

### 2. Procedural Memory

Procedural memory captures domain-specific knowledge and regulatory procedures extracted from the EU AI Act, including:

* Regulatory concepts and definitions
* Compliance requirements

This memory guides the ontology generation process using regulatory knowledge embedded in the source documents.

## Workflow

1. Extract knowledge from the EU AI Act.
2. Retrieve relevant ontology patterns from declarative memory.
3. Retrieve domain-specific procedures from procedural memory.
4. Generate ontology classes, properties, and relationships.
5. Validate generated structures against stored ontology rules.
6. Refine and extend the ontology iteratively.

## Basic Metrics
```bash
python metrics/basic_metrics.py ontology/proof_of_concept_ontology_v0.2.ttl -f turtle -o metrics.csv
```

## Use Case

The framework is designed for regulatory and compliance-oriented ontology development, with an initial focus on the EU AI Act. The approach can be extended to other legal, policy, and domain-specific documents.

## Future Work

* Integration of additional memory types (e.g., episodic memory)
* Multi-document regulatory ontology generation
* Automated ontology alignment and merging
* Support for continuous ontology updates from evolving regulations

## License

MIT
