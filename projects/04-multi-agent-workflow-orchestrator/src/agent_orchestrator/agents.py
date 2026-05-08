from __future__ import annotations

from agent_orchestrator.models import AgentAction, Task


class Agent:
    name = "agent"
    capabilities: set[str] = set()

    def can_handle(self, task: Task) -> bool:
        return task.capability in self.capabilities

    def run(self, task: Task) -> AgentAction:
        raise NotImplementedError


class ResearchAgent(Agent):
    name = "research-agent"
    capabilities = {"research", "retrieval"}

    def run(self, task: Task) -> AgentAction:
        return AgentAction(
            task_id=task.id,
            agent=self.name,
            status="completed",
            output=f"Collected context for '{task.title}' from {task.inputs.get('source', 'local knowledge')}.",
        )


class ImplementationAgent(Agent):
    name = "implementation-agent"
    capabilities = {"implementation", "automation"}

    def run(self, task: Task) -> AgentAction:
        return AgentAction(
            task_id=task.id,
            agent=self.name,
            status="completed",
            output=f"Prepared implementation plan for '{task.title}' with reversible steps.",
            approval_required=task.risk == "high",
        )


class ReviewAgent(Agent):
    name = "review-agent"
    capabilities = {"review", "validation"}

    def run(self, task: Task) -> AgentAction:
        return AgentAction(
            task_id=task.id,
            agent=self.name,
            status="completed",
            output=f"Reviewed '{task.title}' for correctness, risk, and missing tests.",
        )


class ApprovalAgent:
    name = "approval-agent"

    def evaluate(self, action: AgentAction, task: Task) -> AgentAction:
        approved = task.risk != "high" or task.inputs.get("approval") == "granted"
        status = "approved" if approved else "blocked"
        return AgentAction(
            task_id=action.task_id,
            agent=action.agent,
            status=status,
            output=action.output if approved else f"Blocked '{task.title}' until human approval is granted.",
            approval_required=action.approval_required,
            approved=approved,
        )
