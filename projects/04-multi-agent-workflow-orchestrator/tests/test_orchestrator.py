import unittest
from pathlib import Path

from agent_orchestrator.loader import load_workflow
from agent_orchestrator.orchestrator import WorkflowOrchestrator
from agent_orchestrator.planner import LLMPlanner


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class WorkflowOrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = load_workflow(PROJECT_ROOT / "data" / "sample_workflow.json")
        self.report = WorkflowOrchestrator().run(self.workflow)

    def test_workflow_completes_with_approval_gate(self) -> None:
        self.assertEqual(self.report.status, "completed")
        self.assertTrue(any(action.approval_required for action in self.report.actions))
        self.assertTrue(any(event.actor == "approval-agent" for event in self.report.audit_log))

    def test_planner_orders_research_before_implementation_and_review(self) -> None:
        task_order = [action.task_id for action in self.report.actions]

        self.assertEqual(task_order, ["task-1", "task-2", "task-3"])

    def test_llm_planner_prompt_package_is_policy_aware(self) -> None:
        prompt = LLMPlanner("production-model").build_prompt_package(self.workflow)

        self.assertEqual(prompt["model"], "production-model")
        self.assertEqual(len(prompt["tasks"]), 3)
        self.assertTrue(any("approval" in item.lower() for item in prompt["constraints"]))


if __name__ == "__main__":
    unittest.main()
