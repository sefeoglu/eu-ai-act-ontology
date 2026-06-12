"""Tests for the prototype pipeline and ontology memory flow."""

import unittest
from pathlib import Path

from src.client.ui import PrototypeUI
from src.memory.declarative_memory import DeclarativeMemory
from src.memory.memory_generator import MemoryGenerator
from src.server.onto_generator_server import OntologyGenerator


class TestDeclarativeMemory(unittest.TestCase):
    def test_default_ontology_loads(self) -> None:
        mem = DeclarativeMemory().load_default()
        self.assertGreater(mem.triple_count(), 0)

    def test_load_from_none_uses_default(self) -> None:
        mem = DeclarativeMemory().load_from_path(None)
        self.assertGreater(mem.triple_count(), 0)


class TestOntologyGenerator(unittest.TestCase):
    def setUp(self) -> None:
        mem = DeclarativeMemory().load_default()
        self.generator = OntologyGenerator(memory=mem)

    def test_extract_concepts_returns_rows(self) -> None:
        rows = self.generator.extract_concepts(limit=5)
        self.assertGreater(len(rows), 0)
        self.assertIn("label", rows[0])

    def test_validate_ontology(self) -> None:
        result = self.generator.validate_ontology()
        self.assertTrue(result["is_valid"])
        self.assertGreater(result["triple_count"], 0)

    def test_invalid_limit_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.generator.extract_concepts(limit=0)

    def test_invalid_limit_type_raises(self) -> None:
        with self.assertRaises(TypeError):
            self.generator.extract_concepts(limit="five")  # type: ignore[arg-type]


class TestMemoryGenerator(unittest.TestCase):
    def test_split_text_basic(self) -> None:
        chunks = MemoryGenerator().split_text_into_chunks("abcdefghij", chunk_size=4)
        self.assertEqual(chunks, ["abcd", "efgh", "ij"])

    def test_split_text_empty(self) -> None:
        self.assertEqual(MemoryGenerator().split_text_into_chunks(""), [])

    def test_split_text_smaller_than_chunk(self) -> None:
        self.assertEqual(
            MemoryGenerator().split_text_into_chunks("hi", chunk_size=100), ["hi"]
        )

    def test_split_text_unicode(self) -> None:
        result = MemoryGenerator().split_text_into_chunks("öğrenci", chunk_size=3)
        self.assertEqual(result, ["öğr", "enc", "i"])

    def test_invalid_chunk_size_raises(self) -> None:
        with self.assertRaises(ValueError):
            MemoryGenerator().split_text_into_chunks("abc", chunk_size=0)


class TestPrototypePipeline(unittest.TestCase):
    """End-to-end tests for the full pipeline via PrototypeUI."""

    def setUp(self) -> None:
        self.ui = PrototypeUI()  # uses bundled defaults

    def test_pipeline_list_concepts(self) -> None:
        report = self.ui.run_pipeline("list concepts")
        self.assertEqual(report["plan"]["action"], "extract_concepts")
        self.assertTrue(report["validation"]["is_valid"])
        self.assertIsInstance(report["result"], list)

    def test_pipeline_validate_ontology(self) -> None:
        report = self.ui.run_pipeline("validate ontology")
        self.assertEqual(report["plan"]["action"], "validate_ontology")
        self.assertTrue(report["validation"]["is_valid"])
        self.assertTrue(report["result"]["is_valid"])

    def test_pipeline_show_mappings(self) -> None:
        report = self.ui.run_pipeline("show mappings")
        self.assertTrue(report["validation"]["is_valid"])
        self.assertIsInstance(report["result"], dict)

    def test_memory_info_in_report(self) -> None:
        report = self.ui.run_pipeline("list concepts")
        mem_info = report["memory"]
        self.assertIn("declarative_source", mem_info)
        self.assertGreater(mem_info["declarative_triples"], 0)
        self.assertIn("procedural_source", mem_info)

    def test_pipeline_custom_ontology_path(self) -> None:
        from src.utils import data_path
        airo_path = data_path("memory", "declarative_memory", "airo.owl")
        ui = PrototypeUI(declarative_ontology_path=airo_path)
        report = ui.run_pipeline("validate ontology")
        self.assertTrue(report["result"]["is_valid"])
        self.assertIn("airo.owl", report["memory"]["declarative_source"])

    def test_pipeline_unknown_goal_defaults_to_extract(self) -> None:
        report = self.ui.run_pipeline("something completely unknown")
        self.assertEqual(report["plan"]["action"], "extract_concepts")


if __name__ == "__main__":
    unittest.main()
