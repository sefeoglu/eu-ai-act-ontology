"""Shared memory primitives backed by RDF graphs."""

from pathlib import Path
<<<<<<< HEAD
from typing import Dict, List, Optional
=======
from typing import Dict, List
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7

from rdflib import Graph


class OntologyMemory:
<<<<<<< HEAD
    """In-memory wrapper around an RDFLib graph."""

    def __init__(self) -> None:
        self.graph: Graph = Graph()
        self.source_path: Optional[Path] = None

    def load(self, ontology_path: Path) -> "OntologyMemory":
        """Parse an ontology file and populate the internal graph.

        The format is determined by reading the first non-whitespace bytes so
        that Turtle files with a ``.owl`` extension are handled correctly.
        """
        path = Path(ontology_path)
        with open(path, "rb") as fh:
            head = fh.read(64).lstrip()
        # Turtle/N3 files start with a '@' directive or a '<' IRI reference
        # followed by whitespace and a predicate that is not an XML tag.
        # RDF/XML always begins with either a BOM, '<?xml', or '<rdf:'.
        if head.startswith((b"<?xml", b"<rdf:", b"<owl:", b"\xef\xbb\xbf")):
            fmt = "xml"
        else:
            fmt = "turtle"
        self.graph.parse(str(path), format=fmt)
        self.source_path = path
        return self

    def run_query(self, query: str) -> List[Dict[str, str]]:
        """Execute a SPARQL SELECT and return stringified bindings."""
=======
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
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
        results = self.graph.query(query)
        rows: List[Dict[str, str]] = []
        for row in results:
            rows.append({
<<<<<<< HEAD
                str(var): str(row[i])
                for i, var in enumerate(results.vars)
                if row[i] is not None
=======
                str(variable): str(row[index])
                for index, variable in enumerate(results.vars)
                if row[index] is not None
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
            })
        return rows

    def triple_count(self) -> int:
<<<<<<< HEAD
        """Return the total triple count of the loaded graph."""
=======
        """Return total triple count."""
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
        return len(self.graph)
