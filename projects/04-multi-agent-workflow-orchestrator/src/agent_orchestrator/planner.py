from __future__ import annotations

from typing import Protocol

from agent_orchestrator.models import Task, Workflow


class WorkflowPlanner(Protocol):
    def plan(self, workflow: Workflow) -> list[Task]:
        """Return ordered tasks for execution."""


class DeterministicPlanner:
    def plan(self, workflow: Workflow) -> list[Task]:
        priority = {"research": 1, "retrieval": 1, "implementation": 2, "automation": 2, "review": 3, "validation": 3}
        return sorted(workflow.tasks, key=lambda task: priority.get(task.capability, 99))


class LLMPlanner:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def plan(self, workflow: Workflow) -> list[Task]:
        prompt_package = self.build_prompt_package(workflow)
        raise NotImplementedError(
            "Connect this boundary to an LLM planner and validate the plan against "
            f"{len(prompt_package['tasks'])} declared tasks and approval policies."
        )

    def build_prompt_package(self, workflow: Workflow) -> dict[str, object]:
        return {
            "model": self.model_name,
            "task": "Order workflow tasks and assign agent capabilities.",
            "goal": workflow.goal,
            "constraints": [
                "Do not invent tasks.",
                "Place research before implementation.",
                "Place review after implementation.",
                "Mark high-risk work for human approval.",
                "Return only task ids in execution order.",
            ],
            "tasks": [task.__dict__ for task in workflow.tasks],
        }
