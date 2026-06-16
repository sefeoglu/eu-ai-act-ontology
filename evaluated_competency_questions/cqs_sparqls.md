# SPARQL Queries

## a) Which high-risk AI systems are represented in the ontology?


```sparql
PREFIX euai: <http://example.org/eu-ai-act#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?system ?label
WHERE {
  ?system a euai:high_risk_ai_system .
  OPTIONAL {
    ?system rdfs:label ?label .
  }
}
ORDER BY ?label
```
### Results

```bash
http://example.org/eu-ai-act#recruitment_screening_ai Recruitment Screening AI
```

---

## b) Which compliance-related activities, documentation requirements, and risk-management measures are associated with AI providers?


```sparql

PREFIX euai: <http://example.org/eu-ai-act#>

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

### Results
```bash
http://example.org/eu-ai-act#model_provider_omega http://example.org/eu-ai-act#draws_up_technical_documentation http://example.org/eu-ai-act#technical_documentation
http://example.org/eu-ai-act#model_provider_omega http://example.org/eu-ai-act#provides_model_information http://example.org/eu-ai-act#model_information
http://example.org/eu-ai-act#model_provider_omega http://www.w3.org/1999/02/22-rdf-syntax-ns#type http://example.org/eu-ai-act#provider
http://example.org/eu-ai-act#model_provider_omega http://www.w3.org/2000/01/rdf-schema#comment Representative provider of a general-purpose AI model. Source: Generated from provided triples.
http://example.org/eu-ai-act#model_provider_omega http://www.w3.org/2000/01/rdf-schema#label Model Provider Omega
http://example.org/eu-ai-act#provider_alpha http://www.w3.org/1999/02/22-rdf-syntax-ns#type http://example.org/eu-ai-act#provider
http://example.org/eu-ai-act#provider_alpha http://www.w3.org/2000/01/rdf-schema#comment Representative provider individual. Source: Generated from provided individuals.
http://example.org/eu-ai-act#provider_alpha http://www.w3.org/2000/01/rdf-schema#label Provider Alpha
```


---

## c) Which transparency obligations are represented in the ontology, and do they require disclosure?

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
### Results
``` bash
http://example.org/eu-ai-act#chat_assistant_disclosure Chat assistant disclosure true
```

