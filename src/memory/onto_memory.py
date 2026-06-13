"""Shared memory primitives backed by RDF graphs."""
from pathlib import Path
from typing import Dict, List, Optional

from rdflib import Graph, RDF, RDFS, OWL
from rdflib.term import Node


class OntologyMemory:
    """In-memory wrapper around an RDFLib graph."""

    def __init__(self) -> None:
        self.graph: Graph = Graph()
        self.source_path: Optional[Path] = None

    def load(self, ontology_path: Path) -> "OntologyMemory":
        """Parse an ontology file and populate the internal graph."""
        path = Path(ontology_path)

        with open(path, "rb") as fh:
            head = fh.read(256)

        head = head.lstrip()

        if head.startswith(b"\xef\xbb\xbf"):
            head = head[3:].lstrip()

        if head.startswith((b"<?xml", b"<rdf:", b"<owl:")):
            fmt = "xml"
        elif head.startswith((b"@prefix", b"@base", b"PREFIX", b"BASE")):
            fmt = "turtle"
        else:
            fmt = None

        self.graph.parse(str(path), format=fmt)
        self.source_path = path
        return self

    def run_query(self, query: str) -> List[Dict[str, str]]:
        """Execute a SPARQL SELECT and return stringified bindings."""
        results = self.graph.query(query)

        rows: List[Dict[str, str]] = []
        for row in results:
            rows.append({
                str(var): str(row[i])
                for i, var in enumerate(results.vars)
                if row[i] is not None
            })

        return rows

    def triple_count(self) -> int:
        """Return the total triple count of the loaded graph."""
        return len(self.graph)

    def get_label(self, node: Node) -> str:
        """Return rdfs:label if available, otherwise local URI name."""
        label = self.graph.value(node, RDFS.label)

        if label is not None:
            return str(label)

        text = str(node)
        return text.rsplit("#", 1)[-1].rsplit("/", 1)[-1]

    def get_classes(self) -> List[str]:
        """Return ontology class URIs."""
        classes = set()

        classes.update(self.graph.subjects(RDF.type, OWL.Class))
        classes.update(self.graph.subjects(RDF.type, RDFS.Class))

        return sorted(str(cls) for cls in classes)

    def get_classes_with_labels(self) -> List[Dict[str, str]]:
        """Return ontology classes with labels."""
        classes = set()

        classes.update(self.graph.subjects(RDF.type, OWL.Class))
        classes.update(self.graph.subjects(RDF.type, RDFS.Class))

        return [
            {
                "uri": str(cls),
                "label": self.get_label(cls),
            }
            for cls in sorted(classes, key=str)
        ]

    def get_properties(self) -> List[str]:
        """Return ontology property URIs."""
        property_types = [
            RDF.Property,
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.AnnotationProperty,
            OWL.FunctionalProperty,
            OWL.InverseFunctionalProperty,
            OWL.TransitiveProperty,
            OWL.SymmetricProperty,
        ]

        properties = set()

        for property_type in property_types:
            properties.update(self.graph.subjects(RDF.type, property_type))

        return sorted(str(prop) for prop in properties)

    def get_properties_with_labels(self) -> List[Dict[str, str]]:
        """Return ontology properties with labels."""
        property_types = [
            RDF.Property,
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.AnnotationProperty,
            OWL.FunctionalProperty,
            OWL.InverseFunctionalProperty,
            OWL.TransitiveProperty,
            OWL.SymmetricProperty,
        ]

        properties = set()

        for property_type in property_types:
            properties.update(self.graph.subjects(RDF.type, property_type))

        return [
            {
                "uri": str(prop),
                "label": self.get_label(prop),
            }
            for prop in sorted(properties, key=str)
        ]