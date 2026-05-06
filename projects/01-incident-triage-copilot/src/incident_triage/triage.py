from __future__ import annotations

from incident_triage.models import Alert, DeployEvent, LogEvent, Runbook, TriageReport
from incident_triage.retrieval import ContextRetriever, RetrievedContext


class TriageEngine:
    """Deterministic triage engine with an LLM-ready boundary."""

    def __init__(self, logs: list[LogEvent], runbooks: list[Runbook], deploys: list[DeployEvent]) -> None:
        self.logs = logs
        self.runbooks = runbooks
        self.deploys = deploys
        self.retriever = ContextRetriever(logs, runbooks, deploys)

    def triage(self, alert: Alert) -> TriageReport:
        context = self.retriever.retrieve(alert)
        relevant_runbooks = self._matching_runbooks(context)
        suspected_causes = self._suspected_causes(alert, context)
        actions = self._recommended_actions(alert, relevant_runbooks, context)
        confidence = self._confidence(context)

        summary = (
            f"{alert.service} is firing `{alert.title}` with {alert.metric} at "
            f"{alert.value:g}, above the {alert.threshold:g} threshold over "
            f"{alert.window_minutes} minutes. The strongest evidence points to "
            f"{suspected_causes[0].lower()}"
        )

        escalation = (
            relevant_runbooks[0].escalation
            if relevant_runbooks
            else "Escalate to the service owner and incident commander for manual assessment."
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

    def _matching_runbooks(self, context: RetrievedContext) -> list[Runbook]:
        titles = {item.title for item in context.runbooks}
        return [runbook for runbook in self.runbooks if runbook.title in titles]

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

        deduped = []
        seen = set()
        for action in actions:
            if action not in seen:
                deduped.append(action)
                seen.add(action)
        return deduped[:6]

    def _confidence(self, context: RetrievedContext) -> float:
        evidence = context.all_evidence
        if not evidence:
            return 0.15
        average = sum(item.score for item in evidence) / len(evidence)
        diversity_bonus = 0.08 * len({item.source for item in evidence})
        return round(min(0.95, average + diversity_bonus), 2)
