"""Tests for the ontology artifact and offline pipeline flow."""

import unittest

from src.client.client_access import PrototypeUI
from src.host.llm_planner import LLMPlanner
from src.memory.declarative_memory import DeclarativeMemory
from src.memory.onto_memory import OntologyMemory
from src.memory.procedural_memory import ProceduralMemory
from src.server.onto_generator_server import OntologyGenerator
from src.utils import data_path


class TestDeclarativeMemory(unittest.TestCase):
    def test_default_ontology_loads(self) -> None:
        mem = DeclarativeMemory().load_default()
        self.assertGreater(mem.triple_count(), 0)


class TestProofOfConceptOntology(unittest.TestCase):
    def setUp(self) -> None:
        self.ontology = OntologyMemory().load(
            data_path("ontology", "proof_of_concept_ontology.ttl")
        )

    def test_proof_of_concept_ontology_parses(self) -> None:
        self.assertGreater(self.ontology.triple_count(), 0)

    def test_prohibited_practices_have_article_references(self) -> None:
        rows = self.ontology.run_query(
            """
            PREFIX aia: <https://w3id.org/eu-ai-act-poc#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?practice ?label ?article WHERE {
              ?practice a aia:ProhibitedAISystem ;
                        rdfs:label ?label ;
                        aia:articleReference ?article .
            }
            """
        )
        self.assertGreaterEqual(len(rows), 4)

    def test_high_risk_areas_have_annex_references(self) -> None:
        rows = self.ontology.run_query(
            """
            PREFIX aia: <https://w3id.org/eu-ai-act-poc#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?systemArea ?label ?annex WHERE {
              ?systemArea a aia:HighRiskAISystem ;
                          rdfs:label ?label ;
                          aia:annexReference ?annex .
            }
            """
        )
        self.assertGreaterEqual(len(rows), 4)


class TestPlannerAndValidation(unittest.TestCase):
    def test_planner_normalizes_space_separated_goal(self) -> None:
        plan = LLMPlanner().create_plan("validate ontology")
        self.assertEqual(plan["action"], "validate_ontology")

    def test_validate_ontology_uses_proof_of_concept_file(self) -> None:
        generator = OntologyGenerator(
            declarative_memory=DeclarativeMemory().load_default(),
            procedural_memory=ProceduralMemory(),
            output_path=data_path("ontology", "proof_of_concept_ontology.ttl"),
        )
        result = generator.validate_ontology()
        self.assertTrue(result["is_valid"])
        self.assertIn("proof_of_concept_ontology.ttl", result["source"])


class TestPrototypePipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.ui = PrototypeUI()

    def test_pipeline_validate_ontology(self) -> None:
        report = self.ui.run_pipeline("validate ontology")
        self.assertEqual(report["plan"]["action"], "validate_ontology")
        self.assertTrue(report["validation"]["is_valid"])
        self.assertTrue(report["result"]["is_valid"])
        self.assertIn("proof_of_concept_ontology.ttl", report["result"]["source"])

    def test_pipeline_multiple_goals_returns_list(self) -> None:
        reports = self.ui.run_pipeline(["memory_generation", "validate_ontology"])
        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0]["plan"]["action"], "memory_generation")
        self.assertEqual(reports[1]["plan"]["action"], "validate_ontology")


if __name__ == "__main__":
    unittest.main()
