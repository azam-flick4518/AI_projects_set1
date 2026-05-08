from __future__ import annotations

import json
from pathlib import Path

from agent_orchestrator.models import Task, Workflow


def load_workflow(path: str | Path) -> Workflow:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return Workflow(
        id=payload["id"],
        goal=payload["goal"],
        tasks=[
            Task(
                id=item["id"],
                title=item["title"],
                capability=item["capability"],
                risk=item["risk"],
                inputs=item.get("inputs", {}),
            )
            for item in payload["tasks"]
        ],
    )
