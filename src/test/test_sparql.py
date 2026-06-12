"""Tests for the prototype ontology memory flow."""

import unittest

from src.memory.declarative_memory import DeclarativeMemory
from src.memory.memory_generator import MemoryGenerator
from src.server.onto_generator_server import OntologyGenerator


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

    def test_text_chunking(self):
        chunks = MemoryGenerator().split_text_into_chunks("abcdefghij", chunk_size=4)
        self.assertEqual(chunks, ["abcd", "efgh", "ij"])

    def test_invalid_chunk_size_raises(self):
        with self.assertRaises(ValueError):
            MemoryGenerator().split_text_into_chunks("abc", chunk_size=0)

    def test_text_chunking_edge_cases(self):
        generator = MemoryGenerator()
        self.assertEqual(generator.split_text_into_chunks("", chunk_size=4), [])
        self.assertEqual(generator.split_text_into_chunks("ab", chunk_size=10), ["ab"])
        self.assertEqual(generator.split_text_into_chunks("öğrenci", chunk_size=3), ["öğr", "enc", "i"])


if __name__ == "__main__":
    unittest.main()
