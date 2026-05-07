from __future__ import annotations

from typing import Protocol

from incident_triage.models import Alert, Evidence, Runbook, TriageReport
from incident_triage.retrieval import RetrievedContext


class ReportSynthesizer(Protocol):
    def synthesize(
        self,
        alert: Alert,
        context: RetrievedContext,
        runbooks: list[Runbook],
    ) -> TriageReport:
        """Create a grounded incident report from retrieved context."""


class DeterministicSynthesizer:
    """Local synthesizer used for demos, tests, and regression baselines."""

    def synthesize(
        self,
        alert: Alert,
        context: RetrievedContext,
        runbooks: list[Runbook],
    ) -> TriageReport:
        suspected_causes = self._suspected_causes(alert, context)
        actions = self._recommended_actions(alert, runbooks, context)
        confidence = self._confidence(context)
        escalation = (
            runbooks[0].escalation
            if runbooks
            else "Escalate to the service owner and incident commander for manual assessment."
        )

        summary = (
            f"{alert.service} is firing `{alert.title}` with {alert.metric} at "
            f"{alert.value:g}, above the {alert.threshold:g} threshold over "
            f"{alert.window_minutes} minutes. The strongest evidence points to "
            f"{suspected_causes[0].lower()}"
        )

        return TriageReport(
            alert_id=alert.id,
            service=alert.service,
            severity=alert.severity,
            summary=summary,
            suspected_causes=suspected_causes,
            recommended_actions=actions,
            escalation=escalation,
            confidence=confidence,
            evidence=context.all_evidence,
            assumptions=[
                "Sample data is treated as the complete incident context for this local demo.",
                "Timestamps are assumed to be close enough to the alert window to be operationally relevant.",
                "Recommendations are limited to runbook-backed or evidence-backed actions.",
            ],
        )

    def _suspected_causes(self, alert: Alert, context: RetrievedContext) -> list[str]:
        causes = []
        if context.deploys and context.deploys[0].score >= 0.6:
            causes.append(f"Recent deploy may have changed behavior for {alert.service}.")
        if any("token" in evidence.detail.lower() for evidence in context.logs):
            causes.append("Payment token validation failures are correlated with the alert.")
        if any("timeout" in evidence.detail.lower() for evidence in context.logs):
            causes.append("Downstream timeout errors may be increasing request failures.")
        if not causes:
            causes.append("The alert is service-correlated, but available evidence is not specific enough.")
        return causes

    def _recommended_actions(
        self,
        alert: Alert,
        runbooks: list[Runbook],
        context: RetrievedContext,
    ) -> list[str]:
        actions: list[str] = []
        for runbook in runbooks:
            actions.extend(runbook.checks[:2])
            actions.extend(runbook.mitigations[:2])

        if context.deploys:
            actions.append(f"Review deploy `{context.deploys[0].title}` and prepare rollback criteria.")
        if not actions:
            actions.append(f"Open an incident channel for {alert.service} and assign an owner.")

        return self._dedupe(actions)[:6]

    def _dedupe(self, values: list[str]) -> list[str]:
        deduped = []
        seen = set()
        for value in values:
            if value not in seen:
                deduped.append(value)
                seen.add(value)
        return deduped

    def _confidence(self, context: RetrievedContext) -> float:
        evidence = context.all_evidence
        if not evidence:
            return 0.15
        average = sum(item.score for item in evidence) / len(evidence)
        diversity_bonus = 0.08 * len({item.source for item in evidence})
        return round(min(0.95, average + diversity_bonus), 2)


class LLMSynthesizer:
    """Production extension point for model-backed incident report synthesis.

    This class intentionally does not call a provider. It defines the boundary:
    production code would send the grounded prompt package to an LLM, parse the
    structured response, then validate that every claim maps back to evidence.
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def synthesize(
        self,
        alert: Alert,
        context: RetrievedContext,
        runbooks: list[Runbook],
    ) -> TriageReport:
        prompt_package = self.build_prompt_package(alert, context, runbooks)
        raise NotImplementedError(
            "Connect this boundary to an LLM provider, then validate the structured "
            f"response against {len(prompt_package['evidence'])} evidence items."
        )

    def build_prompt_package(
        self,
        alert: Alert,
        context: RetrievedContext,
        runbooks: list[Runbook],
    ) -> dict[str, object]:
        return {
            "model": self.model_name,
            "task": "Create a concise incident triage report using only supplied evidence.",
            "constraints": [
                "Do not invent services, deploys, logs, metrics, or actions.",
                "Tie each suspected cause to evidence.",
                "Prefer runbook mitigations over free-form recommendations.",
                "Ask for human approval before rollback, failover, or policy bypass.",
                "Return a structured response matching the TriageReport schema.",
            ],
            "alert": {
                "id": alert.id,
                "service": alert.service,
                "title": alert.title,
                "severity": alert.severity,
                "metric": alert.metric,
                "value": alert.value,
                "threshold": alert.threshold,
                "window_minutes": alert.window_minutes,
                "tags": alert.tags,
            },
            "evidence": [self._evidence_payload(item) for item in context.all_evidence],
            "runbooks": [
                {
                    "id": runbook.id,
                    "service": runbook.service,
                    "title": runbook.title,
                    "checks": runbook.checks,
                    "mitigations": runbook.mitigations,
                    "escalation": runbook.escalation,
                }
                for runbook in runbooks
            ],
        }

    def _evidence_payload(self, evidence: Evidence) -> dict[str, object]:
        return {
            "source": evidence.source,
            "title": evidence.title,
            "detail": evidence.detail,
            "score": evidence.score,
        }
