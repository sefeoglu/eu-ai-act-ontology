"""Tests for the prototype ontology memory flow."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from memory.declarative_memory import DeclarativeMemory
from server.onto_generator_server import OntologyGenerator


class TestSparqlQueries(unittest.TestCase):
    def test_default_ontology_loads(self):
        memory = DeclarativeMemory()
        memory.load_default()
        self.assertGreater(memory.triple_count(), 0)

    def test_concept_query_returns_rows(self):
        generator = OntologyGenerator()
        rows = generator.extract_concepts(limit=5)
        self.assertGreater(len(rows), 0)
        self.assertIn("label", rows[0])


if __name__ == "__main__":
    unittest.main()
