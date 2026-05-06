import unittest
from pathlib import Path

from incident_triage.io import load_alert, load_deploys, load_logs, load_runbooks
from incident_triage.triage import TriageEngine


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TriageEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alert = load_alert(PROJECT_ROOT / "data" / "sample_alert.json")
        self.engine = TriageEngine(
            logs=load_logs(PROJECT_ROOT / "data" / "sample_logs.json"),
            runbooks=load_runbooks(PROJECT_ROOT / "data" / "runbooks.json"),
            deploys=load_deploys(PROJECT_ROOT / "data" / "deploys.json"),
        )

    def test_report_connects_alert_to_deploy_and_token_failure(self) -> None:
        report = self.engine.triage(self.alert)

        self.assertEqual(report.alert_id, "inc-2026-05-06-001")
        self.assertGreaterEqual(report.confidence, 0.65)
        self.assertTrue(any("Recent deploy" in cause for cause in report.suspected_causes))
        self.assertTrue(any("token validation" in cause.lower() for cause in report.suspected_causes))
        self.assertTrue(any("rollback" in action.lower() for action in report.recommended_actions))

    def test_report_includes_diverse_evidence_sources(self) -> None:
        report = self.engine.triage(self.alert)
        sources = {item.source for item in report.evidence}

        self.assertIn("log", sources)
        self.assertIn("runbook", sources)
        self.assertIn("deploy", sources)

    def test_markdown_output_contains_operational_sections(self) -> None:
        report = self.engine.triage(self.alert)
        markdown = report.to_markdown()

        self.assertIn("## Suspected Causes", markdown)
        self.assertIn("## Recommended Actions", markdown)
        self.assertIn("## Evidence", markdown)
        self.assertIn("## Assumptions", markdown)


if __name__ == "__main__":
    unittest.main()
