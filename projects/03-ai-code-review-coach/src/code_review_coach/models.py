from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceFile:
    path: str
    text: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: str
    path: str
    line: int
    message: str
    recommendation: str


@dataclass(frozen=True)
class TestSuggestion:
    path: str
    scenario: str
    reason: str


@dataclass(frozen=True)
class ReviewReport:
    repo_path: str
    summary: str
    findings: list[Finding]
    test_suggestions: list[TestSuggestion]
    assumptions: list[str]

    def to_markdown(self) -> str:
        lines = [
            "# AI Code Review Report",
            "",
            f"Repository: {self.repo_path}",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## Findings",
            "",
        ]
        if self.findings:
            lines.extend(
                f"- [{finding.severity}] {finding.path}:{finding.line} "
                f"{finding.title}: {finding.message} Recommendation: {finding.recommendation}"
                for finding in self.findings
            )
        else:
            lines.append("- No findings.")
        lines.extend(["", "## Test Suggestions", ""])
        if self.test_suggestions:
            lines.extend(
                f"- {suggestion.path}: {suggestion.scenario} ({suggestion.reason})"
                for suggestion in self.test_suggestions
            )
        else:
            lines.append("- No additional test suggestions.")
        lines.extend(["", "## Assumptions", ""])
        lines.extend(f"- {assumption}" for assumption in self.assumptions)
        return "\n".join(lines)
