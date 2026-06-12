"""Prototype ontology generator backed by a loaded DeclarativeMemory."""

import re
from typing import Dict, List

from src.memory.declarative_memory import DeclarativeMemory


class OntologyGenerator:
    """Performs ontology operations over a preloaded DeclarativeMemory graph."""

    def __init__(self, memory: DeclarativeMemory) -> None:
        self.memory = memory

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def extract_concepts(self, limit: int = 10) -> List[Dict[str, str]]:
        """Return up to *limit* labeled ontology concepts."""
        if not isinstance(limit, int):
            raise TypeError("limit must be an integer")
        if limit <= 0 or limit > 1_000:
            raise ValueError(
                f"limit must be between 1 and 1,000 (inclusive), got {limit}"
            )
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?concept ?label WHERE {
          ?concept rdfs:label ?label .
        }
        """
        return self.memory.run_query(query)[:limit]

    def map_to_existing_ontologies(self) -> Dict[str, int]:
        """Return the top namespace occurrence counts in the loaded graph."""
        counts: Dict[str, int] = {}
        for s, _, _ in self.memory.graph:
            ns = str(s).split("#")[0]
            counts[ns] = counts.get(ns, 0) + 1
        return dict(
            sorted(counts.items(), key=lambda item: item[1], reverse=True)[:10]
        )

    def generate_sparql_queries(self) -> Dict[str, str]:
        """Return a catalog of reusable SPARQL queries for the prototype."""
        return {
            "labels": (
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
                "SELECT ?concept ?label WHERE {\n"
                "  ?concept rdfs:label ?label .\n"
                "} LIMIT 20"
            ),
            "class_count": (
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n"
                "SELECT (COUNT(?class) AS ?count) WHERE {\n"
                "  ?class a owl:Class .\n"
                "}"
            ),
        }
    def generate_competency_questions(self, doc_chunk) -> List[str]:
        """Return a list of example competency questions for the loaded ontology."""
        # create competency question based on the content of the procedural memory chunk
        # this is a placeholder implementation; in a real system, this would involve NLP techniques
        text = doc_chunk.get("text", "")    
        

    def generate_owl_ttl(self) -> str:
        """Serialize the loaded graph as Turtle."""
        return self.memory.graph.serialize(format="turtle")

    def validate_ontology(self) -> Dict[str, object]:
        """Run basic health checks over the loaded ontology."""
        triple_count = self.memory.triple_count()
        return {
            "is_valid": triple_count > 0,
            "triple_count": triple_count,
            "source": str(self.memory.source_path),
        }

    def export_github_package(self) -> Dict[str, object]:
        """Return export metadata for future packaging integration."""
        validation = self.validate_ontology()
        return {
            "status": "ready" if validation["is_valid"] else "invalid",
            "triples": validation["triple_count"],
            "source": validation["source"],
        }
    
