from __future__ import annotations

from incident_triage.models import Alert, DeployEvent, LogEvent, Runbook, TriageReport
from incident_triage.retrieval import ContextRetriever, RetrievedContext
from incident_triage.synthesizer import DeterministicSynthesizer, ReportSynthesizer


class TriageEngine:
    """Orchestrates retrieval, runbook selection, and report synthesis."""

    def __init__(
        self,
        logs: list[LogEvent],
        runbooks: list[Runbook],
        deploys: list[DeployEvent],
        synthesizer: ReportSynthesizer | None = None,
    ) -> None:
        self.logs = logs
        self.runbooks = runbooks
        self.deploys = deploys
        self.retriever = ContextRetriever(logs, runbooks, deploys)
        self.synthesizer = synthesizer or DeterministicSynthesizer()

    def triage(self, alert: Alert) -> TriageReport:
        context = self.retriever.retrieve(alert)
        relevant_runbooks = self._matching_runbooks(context)
        return self.synthesizer.synthesize(alert, context, relevant_runbooks)

    def _matching_runbooks(self, context: RetrievedContext) -> list[Runbook]:
        titles = {item.title for item in context.runbooks}
        return [runbook for runbook in self.runbooks if runbook.title in titles]
