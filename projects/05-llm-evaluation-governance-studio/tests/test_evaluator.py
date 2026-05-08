import unittest
from pathlib import Path

from eval_governance.evaluator import Evaluator
from eval_governance.loader import load_cases
from eval_governance.policy import PolicyChecker
from eval_governance.providers import LLMProvider


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class EvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = load_cases(PROJECT_ROOT / "data" / "eval_cases.json")
        self.report = Evaluator().run(self.cases)

    def test_fixture_suite_passes(self) -> None:
        self.assertEqual(self.report.total_cases, 2)
        self.assertEqual(self.report.passed_cases, 2)
        self.assertEqual(self.report.average_score, 1.0)

    def test_policy_checker_flags_missing_citation(self) -> None:
        violations = PolicyChecker().check(
            "checkout-api depends on payments-api",
            requires_citation=True,
            policy_tags=[],
        )

        self.assertIn("missing-citation", violations)

    def test_llm_provider_prompt_package_contains_governance_context(self) -> None:
        provider = LLMProvider("production-model")
        prompt = provider.build_prompt_package(self.cases[0])

        self.assertEqual(prompt["model"], "production-model")
        self.assertEqual(prompt["case_id"], "rag-citation-answer")
        self.assertTrue(prompt["governance_context"]["requires_citation"])


if __name__ == "__main__":
    unittest.main()
