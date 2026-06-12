"""Prototype ontology generator utilities."""

from typing import Dict, List

from src.memory.declarative_memory import DeclarativeMemory


class OntologyGenerator:
    def __init__(self, input_data: dict | None = None):
        self.input_data = input_data or {}
        self.memory = DeclarativeMemory()
        self.memory.load_default()

    def extract_concepts(self, limit: int = 10) -> List[Dict[str, str]]:
        """Extract labeled ontology concepts for quick inspection."""
        if not isinstance(limit, int):
            raise TypeError("limit must be an integer")
        if limit <= 0 or limit > 1_000:
            raise ValueError("limit must be between 1 and 1000 (inclusive)")
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?concept ?label WHERE {
          ?concept rdfs:label ?label .
        }
        """
        return self.memory.run_query(query)[:limit]

    def map_to_existing_ontologies(self) -> Dict[str, int]:
        """Return top namespace counts as a lightweight mapping summary."""
        namespaces: Dict[str, int] = {}
        for subject, _, _ in self.memory.graph:
            namespace = str(subject).split("#")[0]
            namespaces[namespace] = namespaces.get(namespace, 0) + 1
        return dict(sorted(namespaces.items(), key=lambda item: item[1], reverse=True)[:10])

    def generate_owl_ttl(self) -> str:
        """Serialize loaded ontology as Turtle."""
        return self.memory.graph.serialize(format="turtle")

    def generate_sparql_queries(self) -> Dict[str, str]:
        """Return a small query catalog for prototype use."""
        return {
            "labels": """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?concept ?label WHERE {
                  ?concept rdfs:label ?label .
                } LIMIT 20
            """,
            "class_count": """
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                SELECT (COUNT(?class) AS ?count) WHERE {
                  ?class a owl:Class .
                }
            """,
        }

    def validate_ontology(self) -> Dict[str, int | bool]:
        """Perform basic health checks over loaded ontology data."""
        triple_count = self.memory.triple_count()
        has_content = triple_count > 0
        return {
            "is_valid": has_content,
            "triple_count": triple_count,
        }

    def export_github_package(self) -> Dict[str, str | int | bool]:
        """Return export metadata for future packaging integration."""
        validation = self.validate_ontology()
        return {
            "status": "ready" if validation["is_valid"] else "invalid",
            "triples": validation["triple_count"],
            "source": str(self.memory.source_path),
        }
