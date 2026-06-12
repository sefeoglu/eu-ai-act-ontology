# Automated Ontology Development Using a Memory-Based MCP Approach

## Overview

This project presents a Memory-Based Model Context Protocol (MCP) approach for automating ontology development in regulatory domains. The framework leverages different memory components to guide ontology generation, validation, and refinement, reducing manual ontology engineering effort while improving consistency and compliance with domain regulations.

The approach is demonstrated using the EU AI Act as the primary regulatory source.

## Repository Structure

```xml
eu-ai-act-ontology/
├── config/                  # Configuration files
├── doc/                     # Project documentation
├── memory/                  # Bundled memory assets
│   ├── declarative/         # Modelling rules in prompts and reusable ontologies
│   │   ├── existing_ontologies/
│   │   └── prompts/
│   └── procedural/          # Domain-specific regulatory memory
│       └── eu_ai_act_2024/
├── ontology/                # Generated ontology files
├── tests/                   # Unit and integration tests
├── src/
│   ├── client/              # User-facing pipeline entry points
│   ├── host/                # Planning, validation, and agent orchestration
│   ├── memory/              # Memory loading and generation logic
│   ├── server/              # Ontology generation services
│   ├── main.py              # Main application entry point
│   └── utils.py             # Shared utilities
├── requirements.txt         # Python dependencies
└── README.md                # Project overview
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

## Key Features

* Automated ontology generation
* Memory-driven knowledge reuse
* Regulatory knowledge integration
* Consistency validation through ontology rules
* Support for ontology refinement and evolution
* Reduced manual ontology engineering effort

## Use Case

The framework is designed for regulatory and compliance-oriented ontology development, with an initial focus on the EU AI Act. The approach can be extended to other legal, policy, and domain-specific documents.

## Future Work

* Integration of additional memory types (e.g., episodic memory)
* Multi-document regulatory ontology generation
* Automated ontology alignment and merging
* Support for continuous ontology updates from evolving regulations

## License

MIT
