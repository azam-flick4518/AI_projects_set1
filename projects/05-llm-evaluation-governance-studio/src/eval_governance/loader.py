from __future__ import annotations

import json
from pathlib import Path

from eval_governance.models import EvalCase


def load_cases(path: str | Path) -> list[EvalCase]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        EvalCase(
            id=item["id"],
            prompt=item["prompt"],
            expected_contains=item.get("expected_contains", []),
            forbidden_contains=item.get("forbidden_contains", []),
            requires_citation=bool(item.get("requires_citation", False)),
            policy_tags=item.get("policy_tags", []),
        )
        for item in payload
    ]
