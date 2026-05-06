from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from incident_triage.models import Alert, DeployEvent, LogEvent, Runbook

T = TypeVar("T")


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_alert(path: str | Path) -> Alert:
    return Alert.from_dict(read_json(path))


def load_logs(path: str | Path) -> list[LogEvent]:
    return [LogEvent.from_dict(item) for item in read_json(path)]


def load_runbooks(path: str | Path) -> list[Runbook]:
    return [Runbook.from_dict(item) for item in read_json(path)]


def load_deploys(path: str | Path) -> list[DeployEvent]:
    return [DeployEvent.from_dict(item) for item in read_json(path)]
