from __future__ import annotations

from agent_orchestrator.agents import ApprovalAgent, ImplementationAgent, ResearchAgent, ReviewAgent
from agent_orchestrator.models import AgentAction, AuditEvent, Workflow, WorkflowReport
from agent_orchestrator.planner import DeterministicPlanner, WorkflowPlanner


class WorkflowOrchestrator:
    def __init__(self, planner: WorkflowPlanner | None = None) -> None:
        self.planner = planner or DeterministicPlanner()
        self.agents = [ResearchAgent(), ImplementationAgent(), ReviewAgent()]
        self.approver = ApprovalAgent()

    def run(self, workflow: Workflow) -> WorkflowReport:
        audit: list[AuditEvent] = []
        actions: list[AgentAction] = []
        sequence = 1

        planned_tasks = self.planner.plan(workflow)
        audit.append(AuditEvent(sequence, "planner", "planned", f"{len(planned_tasks)} tasks ordered"))
        sequence += 1

        for task in planned_tasks:
            agent = next((candidate for candidate in self.agents if candidate.can_handle(task)), None)
            if agent is None:
                action = AgentAction(task.id, "orchestrator", "skipped", f"No agent supports {task.capability}.")
                actions.append(action)
                audit.append(AuditEvent(sequence, "orchestrator", "skipped", action.output))
                sequence += 1
                continue

            audit.append(AuditEvent(sequence, "orchestrator", "assigned", f"{task.id} -> {agent.name}"))
            sequence += 1
            action = agent.run(task)
            audit.append(AuditEvent(sequence, agent.name, action.status, action.output))
            sequence += 1

            if action.approval_required:
                action = self.approver.evaluate(action, task)
                audit.append(AuditEvent(sequence, self.approver.name, action.status, action.output))
                sequence += 1
            actions.append(action)

        status = "completed" if all(action.status in {"completed", "approved"} for action in actions) else "blocked"
        return WorkflowReport(
            workflow_id=workflow.id,
            goal=workflow.goal,
            status=status,
            actions=actions,
            audit_log=audit,
            assumptions=[
                "Agents are deterministic local role implementations.",
                "High-risk tasks require explicit approval in workflow input.",
                "A production planner can be added behind the LLMPlanner boundary.",
            ],
        )
