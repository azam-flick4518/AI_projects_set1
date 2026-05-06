from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from incident_triage.models import Alert, DeployEvent, Evidence, LogEvent, Runbook


TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def tokenize(value: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(value.lower()))


def overlap_score(query_terms: set[str], candidate: str) -> float:
    candidate_terms = tokenize(candidate)
    if not query_terms or not candidate_terms:
        return 0.0
    overlap = len(query_terms & candidate_terms)
    return overlap / max(len(query_terms), 1)


@dataclass(frozen=True)
class RetrievedContext:
    logs: list[Evidence]
    runbooks: list[Evidence]
    deploys: list[Evidence]

    @property
    def all_evidence(self) -> list[Evidence]:
        return [*self.logs, *self.runbooks, *self.deploys]


class ContextRetriever:
    def __init__(
        self,
        logs: Iterable[LogEvent],
        runbooks: Iterable[Runbook],
        deploys: Iterable[DeployEvent],
    ) -> None:
        self.logs = list(logs)
        self.runbooks = list(runbooks)
        self.deploys = list(deploys)

    def retrieve(self, alert: Alert, limit: int = 4) -> RetrievedContext:
        query = " ".join([alert.service, alert.title, alert.metric, *alert.tags])
        query_terms = tokenize(query)
        return RetrievedContext(
            logs=self._rank_logs(alert, query_terms, limit),
            runbooks=self._rank_runbooks(alert, query_terms, limit=2),
            deploys=self._rank_deploys(alert, query_terms, limit=2),
        )

    def _rank_logs(self, alert: Alert, query_terms: set[str], limit: int) -> list[Evidence]:
        evidence = []
        for log in self.logs:
            service_boost = 0.35 if log.service == alert.service else 0.0
            level_boost = 0.2 if log.level.lower() in {"error", "critical"} else 0.0
            tag_boost = 0.15 if set(alert.tags) & set(log.tags) else 0.0
            score = overlap_score(query_terms, " ".join([log.service, log.message, *log.tags]))
            total = min(1.0, score + service_boost + level_boost + tag_boost)
            if total > 0:
                evidence.append(
                    Evidence(
                        source="log",
                        title=f"{log.level} {log.service} {log.timestamp}",
                        detail=f"{log.message} trace_id={log.trace_id or 'n/a'}",
                        score=round(total, 3),
                    )
                )
        return sorted(evidence, key=lambda item: item.score, reverse=True)[:limit]

    def _rank_runbooks(self, alert: Alert, query_terms: set[str], limit: int) -> list[Evidence]:
        evidence = []
        for runbook in self.runbooks:
            content = " ".join(
                [runbook.service, runbook.title, *runbook.symptoms, *runbook.checks, *runbook.mitigations]
            )
            service_boost = 0.4 if runbook.service == alert.service else 0.0
            score = min(1.0, overlap_score(query_terms, content) + service_boost)
            if score > 0:
                evidence.append(
                    Evidence(
                        source="runbook",
                        title=runbook.title,
                        detail=f"{runbook.id}: {runbook.symptoms[0] if runbook.symptoms else 'general guidance'}",
                        score=round(score, 3),
                    )
                )
        return sorted(evidence, key=lambda item: item.score, reverse=True)[:limit]

    def _rank_deploys(self, alert: Alert, query_terms: set[str], limit: int) -> list[Evidence]:
        evidence = []
        for deploy in self.deploys:
            service_boost = 0.45 if deploy.service == alert.service else 0.0
            risk_boost = 0.15 if set(alert.tags) & set(deploy.risk_tags) else 0.0
            score = overlap_score(query_terms, " ".join([deploy.service, deploy.summary, *deploy.risk_tags]))
            total = min(1.0, score + service_boost + risk_boost)
            if total > 0:
                evidence.append(
                    Evidence(
                        source="deploy",
                        title=f"{deploy.version} by {deploy.author}",
                        detail=f"{deploy.timestamp}: {deploy.summary}",
                        score=round(total, 3),
                    )
                )
        return sorted(evidence, key=lambda item: item.score, reverse=True)[:limit]
