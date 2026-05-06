from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Alert:
    id: str
    service: str
    title: str
    severity: str
    metric: str
    value: float
    threshold: float
    window_minutes: int
    timestamp: str
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Alert":
        return cls(
            id=str(payload["id"]),
            service=str(payload["service"]),
            title=str(payload["title"]),
            severity=str(payload["severity"]),
            metric=str(payload["metric"]),
            value=float(payload["value"]),
            threshold=float(payload["threshold"]),
            window_minutes=int(payload["window_minutes"]),
            timestamp=str(payload["timestamp"]),
            tags=[str(tag) for tag in payload.get("tags", [])],
        )


@dataclass(frozen=True)
class LogEvent:
    timestamp: str
    service: str
    level: str
    message: str
    trace_id: str | None = None
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LogEvent":
        return cls(
            timestamp=str(payload["timestamp"]),
            service=str(payload["service"]),
            level=str(payload["level"]),
            message=str(payload["message"]),
            trace_id=payload.get("trace_id"),
            tags=[str(tag) for tag in payload.get("tags", [])],
        )


@dataclass(frozen=True)
class Runbook:
    id: str
    service: str
    title: str
    symptoms: list[str]
    checks: list[str]
    mitigations: list[str]
    escalation: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Runbook":
        return cls(
            id=str(payload["id"]),
            service=str(payload["service"]),
            title=str(payload["title"]),
            symptoms=[str(item) for item in payload.get("symptoms", [])],
            checks=[str(item) for item in payload.get("checks", [])],
            mitigations=[str(item) for item in payload.get("mitigations", [])],
            escalation=str(payload["escalation"]),
        )


@dataclass(frozen=True)
class DeployEvent:
    id: str
    service: str
    timestamp: str
    version: str
    summary: str
    author: str
    risk_tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DeployEvent":
        return cls(
            id=str(payload["id"]),
            service=str(payload["service"]),
            timestamp=str(payload["timestamp"]),
            version=str(payload["version"]),
            summary=str(payload["summary"]),
            author=str(payload["author"]),
            risk_tags=[str(tag) for tag in payload.get("risk_tags", [])],
        )


@dataclass(frozen=True)
class Evidence:
    source: str
    title: str
    detail: str
    score: float


@dataclass(frozen=True)
class TriageReport:
    alert_id: str
    service: str
    severity: str
    summary: str
    suspected_causes: list[str]
    recommended_actions: list[str]
    escalation: str
    confidence: float
    evidence: list[Evidence]
    assumptions: list[str]

    def to_markdown(self) -> str:
        lines = [
            f"# Incident Triage Report: {self.alert_id}",
            "",
            f"- Service: `{self.service}`",
            f"- Severity: `{self.severity}`",
            f"- Confidence: `{self.confidence:.2f}`",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## Suspected Causes",
            "",
        ]
        lines.extend(f"- {cause}" for cause in self.suspected_causes)
        lines.extend(["", "## Recommended Actions", ""])
        lines.extend(f"- {action}" for action in self.recommended_actions)
        lines.extend(["", "## Escalation", "", self.escalation, "", "## Evidence", ""])
        lines.extend(
            f"- **{item.source}: {item.title}** - {item.detail} (score {item.score:.2f})"
            for item in self.evidence
        )
        lines.extend(["", "## Assumptions", ""])
        lines.extend(f"- {assumption}" for assumption in self.assumptions)
        return "\n".join(lines)
