from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    capability: str
    risk: str
    inputs: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Workflow:
    id: str
    goal: str
    tasks: list[Task]


@dataclass(frozen=True)
class AgentAction:
    task_id: str
    agent: str
    status: str
    output: str
    approval_required: bool = False
    approved: bool = False


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    actor: str
    event: str
    detail: str


@dataclass(frozen=True)
class WorkflowReport:
    workflow_id: str
    goal: str
    status: str
    actions: list[AgentAction]
    audit_log: list[AuditEvent]
    assumptions: list[str]

    def to_markdown(self) -> str:
        lines = [
            "# Multi-Agent Workflow Report",
            "",
            f"Workflow: {self.workflow_id}",
            f"Status: {self.status}",
            "",
            "## Goal",
            "",
            self.goal,
            "",
            "## Actions",
            "",
        ]
        lines.extend(
            f"- {action.task_id} | {action.agent} | {action.status} | "
            f"approval={action.approved}: {action.output}"
            for action in self.actions
        )
        lines.extend(["", "## Audit Log", ""])
        lines.extend(
            f"- {event.sequence}. {event.actor}: {event.event} - {event.detail}"
            for event in self.audit_log
        )
        lines.extend(["", "## Assumptions", ""])
        lines.extend(f"- {assumption}" for assumption in self.assumptions)
        return "\n".join(lines)
