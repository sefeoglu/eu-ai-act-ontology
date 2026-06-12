# EU AI Act proof-of-concept ontology: short documentation

## Scope
This proof-of-concept ontology models selected concepts from Regulation (EU) 2024/1689: AI-system risk categories, prohibited practices, high-risk AI-system areas, regulated actors, authorities, obligations, and compliance artefacts. It is intentionally lightweight: it captures enough structure for navigation, classification, and question-answering, but it does not encode the full legal rule conditions, exceptions, deadlines, penalties, or sector-specific product-safety interactions.

The model uses OWL/Turtle and reuses standard vocabularies where useful: `dcterms` for source metadata, `rdfs:label` for human-readable names, `skos:Concept` for risk-category vocabulary items, `prov` for possible workflow provenance extension, and `odrl:Duty` as a superclass for obligations. Custom annotations `aia:articleReference`, `aia:annexReference`, and `aia:shortDescription` keep each modeled element traceable to the Act.

## AI-assisted pipeline
1. **Legal-text scoping.** I used an LLM to identify candidate entities from the official EU AI Act text: definitions in Article 3, prohibited practices in Article 5, high-risk classification in Article 6 and Annex III, provider obligations in Articles 9–16, deployer obligations in Articles 26–27, transparency duties in Article 50, and authority concepts in Articles 28, 64, and 74.
2. **Ontology drafting.** The LLM proposed a class/property pattern: `AISystem`, `RiskCategory`, `Actor`, `Authority`, `Obligation`, and `ComplianceArtefact`, with obligations linked to systems through `aia:subjectToObligation` and to required artefacts through `aia:requiresArtefact`.
3. **Human-in-the-loop checks.** Outputs were checked against article/annex headings and the official legal text. I deliberately avoided over-formalising vague legal conditions, exceptions, and thresholds that would require legal interpretation.
4. **Validation.** The Turtle file was parsed with `rdflib`, simple metric checks were produced, and the ontology is designed to load in Protégé. No disjointness axioms were added, reducing the risk of unintended unsatisfiable classes in this POC.

## Key modelling decisions
- **Risk categories as both individuals and SKOS concepts.** This supports lightweight querying without committing to a closed legal taxonomy.
- **Prohibited and high-risk examples as named individuals typed by class.** This makes article/annex references easy to query and inspect in Protégé.
- **Obligations as first-class resources.** This supports queries such as “what obligations apply to high-risk systems?” and “which artefacts are required by provider obligations?”
- **Article references as annotations, not legal semantics.** The POC remains explainable while avoiding unsupported automated legal conclusions.

## Competency questions
1. Which AI practices are prohibited under Article 5?
2. Which high-risk system areas are listed from Annex III?
3. What obligations are associated with high-risk AI systems?
4. Which compliance artefacts are required by provider obligations?
5. Which actor classes are represented, and where are their definitions or obligations referenced?

## Example SPARQL queries

### 1. Prohibited practices and article references
```sparql
PREFIX aia: <https://w3id.org/eu-ai-act-poc#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?practice ?label ?article WHERE {
  ?practice a aia:ProhibitedAISystem ;
            rdfs:label ?label ;
            aia:articleReference ?article .
}
ORDER BY ?article
```

### 2. High-risk areas from Annex III
```sparql
PREFIX aia: <https://w3id.org/eu-ai-act-poc#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?systemArea ?label ?annex WHERE {
  ?systemArea a aia:HighRiskAISystem ;
              rdfs:label ?label ;
              aia:annexReference ?annex .
}
ORDER BY ?annex
```

### 3. Obligations and required compliance artefacts
```sparql
PREFIX aia: <https://w3id.org/eu-ai-act-poc#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?obligationLabel ?article ?artefactLabel WHERE {
  ?obligation a aia:ProviderObligation ;
              rdfs:label ?obligationLabel ;
              aia:articleReference ?article ;
              aia:requiresArtefact ?artefact .
  ?artefact rdfs:label ?artefactLabel .
}
ORDER BY ?article
```

## Preliminary evaluation metrics and methods
- **Structural metrics:** number of classes, object properties, datatype properties, annotation properties, individuals, triples, and article-referenced entities.
- **Coverage metrics:** count represented Article 5 prohibitions, Annex III high-risk areas, high-risk provider obligations, deployer obligations, and transparency obligations.
- **Quality checks:** parse validity, missing-label detection, missing-article-reference detection for legally grounded terms, duplicate-label detection, and reasoner consistency in Protégé using HermiT or ELK.
- **Manual evaluation:** sample domain-expert review of 3–5 competency questions and spot-checking each article/annex annotation against the official text.
