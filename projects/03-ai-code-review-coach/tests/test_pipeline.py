import unittest
from pathlib import Path

from code_review_coach.pipeline import CodeReviewPipeline
from code_review_coach.synthesizer import LLMReviewSynthesizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CodeReviewPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = CodeReviewPipeline()
        self.report = self.pipeline.review(str(PROJECT_ROOT / "data" / "sample_repo"))

    def test_detects_security_and_reliability_findings(self) -> None:
        rule_ids = {finding.rule_id for finding in self.report.findings}

        self.assertIn("security-hardcoded-secret", rule_ids)
        self.assertIn("security-dynamic-execution", rule_ids)
        self.assertIn("reliability-broad-except", rule_ids)

    def test_suggests_payment_and_exception_tests(self) -> None:
        scenarios = " ".join(suggestion.scenario for suggestion in self.report.test_suggestions)

        self.assertIn("payment", scenarios.lower())
        self.assertIn("exception", scenarios.lower())

    def test_llm_prompt_package_is_grounded(self) -> None:
        synthesizer = LLMReviewSynthesizer("production-model")
        prompt = synthesizer.build_prompt_package(
            self.report.repo_path,
            self.report.findings,
            self.report.test_suggestions,
        )

        self.assertEqual(prompt["model"], "production-model")
        self.assertGreaterEqual(len(prompt["findings"]), 3)
        self.assertTrue(any("Do not invent" in item for item in prompt["constraints"]))


if __name__ == "__main__":
    unittest.main()
