import unittest
from pathlib import Path

from kg_rag.pipeline import KnowledgeGraphRagPipeline
from kg_rag.synthesizer import LLMAnswerSynthesizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class KnowledgeGraphRagTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = KnowledgeGraphRagPipeline(PROJECT_ROOT / "data" / "corpus")

    def test_graph_extracts_entities_and_relationships(self) -> None:
        graph = self.pipeline.graph
        entity_names = {entity.name for entity in graph.entities.values()}
        relationship_kinds = {relationship.kind for relationship in graph.relationships}

        self.assertIn("checkout-api", entity_names)
        self.assertIn("payments-api", entity_names)
        self.assertIn("customer-data-handling", entity_names)
        self.assertIn("depends_on", relationship_kinds)
        self.assertIn("governed_by", relationship_kinds)

    def test_answer_connects_services_policy_and_citations(self) -> None:
        answer = self.pipeline.answer(
            "Which services depend on payments-api and what policy applies to customer data?"
        )

        self.assertIn("payments-api", answer.summary)
        self.assertIn("customer-data-handling", answer.summary)
        self.assertGreaterEqual(len(answer.citations), 2)
        self.assertTrue(any(fact.relationship == "depends_on" for fact in answer.graph_facts))

    def test_llm_synthesizer_builds_grounded_prompt_package(self) -> None:
        chunks, facts = self.pipeline.retriever.retrieve(
            "Which policy applies to payment tokens?"
        )
        synthesizer = LLMAnswerSynthesizer(model_name="production-model")

        prompt_package = synthesizer.build_prompt_package(
            "Which policy applies to payment tokens?",
            chunks,
            facts,
        )

        self.assertEqual(prompt_package["model"], "production-model")
        self.assertGreaterEqual(len(prompt_package["chunks"]), 1)
        self.assertTrue(
            any("Cite every claim" in constraint for constraint in prompt_package["constraints"])
        )


if __name__ == "__main__":
    unittest.main()
