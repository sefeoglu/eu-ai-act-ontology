from pathlib import Path
from rdflib import Graph


TTL_PATH = "eu-ai-act-ontology/ontology/proof_of_concept_ontology_v0.2.ttl"


SPARQL_QUERIES = {
    "high_risk_ai_systems": """
PREFIX euai: <http://example.org/eu-ai-act#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?system ?label
WHERE {
  ?system a euai:high_risk_ai_system .
  OPTIONAL { ?system rdfs:label ?label . }
}
ORDER BY ?label
""",

    "provider_compliance_documentation_risk": """
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
""",

    "transparency_obligations": """
PREFIX euai: <http://example.org/eu-ai-act#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?obligation ?label ?requiresDisclosure
WHERE {
  ?obligation a euai:transparency_obligation .

  OPTIONAL { ?obligation rdfs:label ?label . }
  OPTIONAL { ?obligation euai:requires_disclosure ?requiresDisclosure . }
}
ORDER BY ?label
"""
}


def load_graph(ttl_path: str | Path) -> Graph:
    graph = Graph()
    graph.parse(ttl_path, format="turtle")
    return graph


def run_query(graph: Graph, query_name: str):
    query = SPARQL_QUERIES[query_name]
    return graph.query(query)


def print_results(graph: Graph, query_name: str) -> None:
    print(f"\n=== {query_name} ===")

    for row in run_query(graph, query_name):
        print(*row)


def run_all_queries(graph: Graph) -> None:
    print("Triples:", len(graph))

    for query_name in SPARQL_QUERIES:
        print_results(graph, query_name)


def main() -> None:
    graph = load_graph(TTL_PATH)
    run_all_queries(graph)


if __name__ == "__main__":
    main()