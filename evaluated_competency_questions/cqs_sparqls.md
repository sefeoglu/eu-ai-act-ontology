# SPARQL Queries

## a) Which AI systems are classified as high-risk under the EU AI Act?

This query retrieves all entities classified as `HighRiskAISystem` together with their labels (if available).

```sparql
PREFIX euai: <http://example.org/eu-ai-act#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?system ?label
WHERE {
  ?system a euai:HighRiskAISystem .
  OPTIONAL {
    ?system rdfs:label ?label .
  }
}
ORDER BY ?label
```

### Purpose

The query identifies AI systems that fall within the high-risk category under the EU AI Act. Such systems are subject to stricter regulatory requirements due to their potential impact on health, safety, or fundamental rights.

---

## b) What obligations apply to providers of high-risk AI systems?

This query returns obligations that apply specifically to providers of high-risk AI systems.

```sparql
PREFIX euai: <http://example.org/eu-ai-act#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?obligation ?label
WHERE {
  ?obligation a euai:Obligation .
  ?obligation euai:appliesToActor euai:Provider .
  ?obligation euai:appliesToSystemType euai:HighRiskAISystem .

  OPTIONAL {
    ?obligation rdfs:label ?label .
  }
}
ORDER BY ?label
```

### Purpose

The query retrieves regulatory obligations imposed on providers of high-risk AI systems, such as requirements relating to risk management, data governance, technical documentation, transparency, human oversight, accuracy, robustness, and cybersecurity.

---

## c) Which actors are subject to transparency obligations?

This query identifies actors that are linked to at least one transparency obligation.

```sparql
PREFIX euai: <http://example.org/eu-ai-act#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

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

### Purpose

The query determines which categories of actors (e.g., providers, deployers, importers, distributors, or other entities defined in the ontology) are required to comply with transparency-related obligations under the EU AI Act.
