from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    id: str
    prompt: str
    expected_contains: list[str]
    forbidden_contains: list[str]
    requires_citation: bool
    policy_tags: list[str]


@dataclass(frozen=True)
class ModelOutput:
    case_id: str
    text: str


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    passed: bool
    score: float
    missing_expected: list[str]
    forbidden_found: list[str]
    policy_violations: list[str]
    output: str


@dataclass(frozen=True)
class EvalReport:
    total_cases: int
    passed_cases: int
    average_score: float
    results: list[CaseResult]
    assumptions: list[str]

    def to_markdown(self) -> str:
        lines = [
            "# LLM Evaluation Report",
            "",
            f"Cases: {self.passed_cases}/{self.total_cases} passed",
            f"Average score: {self.average_score:.2f}",
            "",
            "## Results",
            "",
        ]
        lines.extend(
            f"- {result.case_id}: {'PASS' if result.passed else 'FAIL'} "
            f"score={result.score:.2f} missing={result.missing_expected} "
            f"forbidden={result.forbidden_found} policy={result.policy_violations}"
            for result in self.results
        )
        lines.extend(["", "## Assumptions", ""])
        lines.extend(f"- {assumption}" for assumption in self.assumptions)
        return "\n".join(lines)
