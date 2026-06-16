# Automated Ontology Development Using a Memory-Based MCP Approach

## 1. Introduction

This project develops an AI assistant tool to generate a domain-specific ontology by automating the Stanford Ontology Development 101 process using a memory-based Model Context Protocol (MCP) approach. The ontology development process follows seven steps:

1. Determining the domain and scope and generating competency questions.
2. Reusing existing ontologies.
3. Enumerating important terms (concept extraction).
4. Defining classes and their hierarchies (concept extraction).
5. Defining properties for classes (concept extraction).
6. Defining domains, ranges, and constraints.
7. Creating instances.

We designed a memory-based MCP that automatically constructs a draft ontology and validates it using a parser and reasoner at the end of the construction process. The protocol follows the ontology development steps listed above. The following section describes the proposed approach in detail.

## 2. Memory-Based Model Context Protocol

The memory-based MCP consists of four main components: **Client**, **Host**, **Server**, and **Memory**.

### 2.1 Client

The Client serves as the interface between the user and the host system, enabling the execution of goals defined within the ontology development process. The client submits these goals to the LLM Planner located in the Host, which orchestrates the tasks required to accomplish them. Upon completion, the system generates a report describing the results and outcomes of the executed goals.

The supported goals include:

- Memory generation (including ontology reuse).
- Competency question generation.
- Ontology generation.
- Concept mapping with existing ontologies.
- Borrowing existing classes from mapped ontologies.
- Validation and consistency checking.

Memory generation is a prerequisite for all ontology development tasks because it provides access to both procedural knowledge (EU AI Act articles) and declarative knowledge (ontology engineering prompts and reused ontologies). These goals are converted into an execution plan by the LLM Planner and subsequently executed by the MCP client.

### 2.2 Host

The Host converts goals into actions, creates execution plans through the LLM Planner, and returns these actions to the Client. The MCP Client triggers the Server to execute the actions.

The Host also contains two agents:

- **Document Crawler Agent**
- **GPT-based Domain Expert Agent**

### 2.3 Server

The Server executes all ontology-generation actions. It communicates with the agents in the Host and invokes the Domain Expert Agent whenever ontology-development tasks require domain-specific reasoning.

### 2.4 Memory

The Memory component contains two types of memory:

- **Procedural Memory**: Contains articles from the EU AI Act 2024 collected by the Document Crawler Agent.
- **Declarative Memory**: Contains ontology development prompts, rules, and reusable ontologies.

The Memory Generator combines procedural and declarative memory into a unified pipeline that can be accessed by the Server. The Ontology Memory component parses existing ontologies and retrieves classes and properties for reuse during ontology construction.

### 2.5 Human-in-the-Loop Refinement

The proposed approach was used to generate an initial draft ontology containing candidate classes, hierarchies, and relationships. The resulting ontology was subsequently refined, validated, and completed through manual ontology engineering to improve conceptual consistency, align the ontology with the EU AI Act, and incorporate annotations and ontology design decisions.

## 3. Evaluation

### 3.1 Data and Settings

#### Existing Ontologies

- AIRO (AI Risk Ontology)
- AIO (Artificial Intelligence Ontology)
- DPV (Data Privacy Vocabulary)
- VAIR (Vocabulary of AI Risk)

#### Documents

- English version of the EU AI Act 2024

#### Large Language Models

- GPT-3.5-Pro (testing)
- GPT-5.4-mini (production)

Additional implementation settings are available in the source code repository.

### 3.2 Competency Questions and SPARQL Queries

The following competency questions were evaluated against the ontology. Complete results are available in the repository.

#### a) Which high-risk AI systems are represented in the ontology?

```sparql
SELECT ?system ?label
WHERE {
  ?system a euai:high_risk_ai_system .
  OPTIONAL {
    ?system rdfs:label ?label .
  }
}
ORDER BY ?label
```

#### b) Which compliance-related activities, documentation requirements, and risk-management measures are associated with AI providers?

```sparql
SELECT ?s ?p ?o
WHERE {
  ?s ?p ?o .
  FILTER(
    CONTAINS(STR(?p), "compliance") ||
    CONTAINS(STR(?p), "documentation") ||
    CONTAINS(STR(?p), "risk") ||
    CONTAINS(STR(?p), "oversight")
  )
}
ORDER BY ?s ?p
```

#### c) Which transparency obligations are represented in the ontology, and do they require disclosure?

```sparql
SELECT DISTINCT ?actor ?label
WHERE {
  ?actor a euai:Actor .
  ?obligation a euai:TransparencyObligation ;
              euai:appliesToActor ?actor .
  OPTIONAL {
    ?actor rdfs:label ?label .
  }
}
ORDER BY ?label
```

### 3.3 Validation and Metrics

#### Validation

The ontology was loaded using `rdflib`, and the HermiT reasoner was executed. In addition, reasoning was performed within Protégé using the HermiT reasoner. Screenshots showing inferred individuals are available in the repository.

#### Structural Metrics

**Before Mapping**

| Metric | Value |
|----------|--------|
| Classes | 290 |
| Object Properties | 78 |
| Data Properties | 18 |
| Total Properties | 96 |
| Individuals | 50 |
| Maximum Hierarchy Depth | 2 |
| Average Hierarchy Breadth | 0.20 |
| Attribute Richness | 0.25 |
| Relationship Density | 0.28 |

**After Mapping**

| Metric | Value |
|----------|--------|
| Classes | 272 |
| Object Properties | 78 |
| Data Properties | 18 |
| Total Properties | 80 |
| Individuals | 51 |
| Maximum Hierarchy Depth | 2 |
| Average Hierarchy Breadth | 0.21 |
| Attribute Richness | 0.27 |
| Relationship Density | 0.29 |

Due to the context-window limitations of large language models, some classes and properties may be removed during the mapping process.