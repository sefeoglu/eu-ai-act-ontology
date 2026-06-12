"""Shared memory primitives backed by RDF graphs."""

from pathlib import Path
from typing import Dict, List

from rdflib import Graph


class OntologyMemory:
    """Simple in-memory wrapper around an RDFLib graph."""

    def __init__(self) -> None:
        self.graph = Graph()
        self.source_path: Path | None = None

    def load(self, ontology_path: Path) -> Graph:
        """Load ontology content from disk."""
        path = Path(ontology_path)
        ontology_format = "xml" if path.suffix.lower() in {".owl", ".rdf", ".xml"} else "turtle"
        self.graph.parse(str(path), format=ontology_format)
        self.source_path = path
        return self.graph

    def run_query(self, query: str) -> List[Dict[str, str]]:
        """Execute SPARQL and return stringified bindings."""
        results = self.graph.query(query)
        rows: List[Dict[str, str]] = []
        for row in results:
            rows.append({
                str(variable): str(row[index])
                for index, variable in enumerate(results.vars)
                if row[index] is not None
            })
        return rows

    def triple_count(self) -> int:
        """Return total triple count."""
        return len(self.graph)
