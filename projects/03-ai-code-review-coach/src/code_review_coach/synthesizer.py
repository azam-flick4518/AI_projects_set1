from __future__ import annotations

from typing import Protocol

from code_review_coach.models import Finding, ReviewReport, TestSuggestion


class ReviewSynthesizer(Protocol):
    def synthesize(
        self,
        repo_path: str,
        findings: list[Finding],
        test_suggestions: list[TestSuggestion],
    ) -> ReviewReport:
        """Create a structured review report from deterministic analysis."""


class DeterministicReviewSynthesizer:
    def synthesize(
        self,
        repo_path: str,
        findings: list[Finding],
        test_suggestions: list[TestSuggestion],
    ) -> ReviewReport:
        high = sum(1 for finding in findings if finding.severity == "high")
        medium = sum(1 for finding in findings if finding.severity == "medium")
        low = sum(1 for finding in findings if finding.severity == "low")
        summary = (
            f"Found {len(findings)} review findings "
            f"({high} high, {medium} medium, {low} low) and "
            f"{len(test_suggestions)} focused test suggestions."
        )
        return ReviewReport(
            repo_path=repo_path,
            summary=summary,
            findings=findings,
            test_suggestions=test_suggestions,
            assumptions=[
                "The local demo scans Python files only.",
                "Findings come from deterministic rules so tests remain stable.",
                "A production LLM should explain impact and draft review comments from these grounded findings.",
            ],
        )


class LLMReviewSynthesizer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def synthesize(
        self,
        repo_path: str,
        findings: list[Finding],
        test_suggestions: list[TestSuggestion],
    ) -> ReviewReport:
        prompt_package = self.build_prompt_package(repo_path, findings, test_suggestions)
        raise NotImplementedError(
            "Connect this boundary to an LLM provider and validate generated review comments "
            f"against {len(prompt_package['findings'])} deterministic findings."
        )

    def build_prompt_package(
        self,
        repo_path: str,
        findings: list[Finding],
        test_suggestions: list[TestSuggestion],
    ) -> dict[str, object]:
        return {
            "model": self.model_name,
            "task": "Write concise, actionable code review notes from supplied findings.",
            "repo_path": repo_path,
            "constraints": [
                "Do not invent files or line numbers.",
                "Prioritize correctness, security, reliability, and missing tests.",
                "Explain impact in plain language.",
                "Use the supplied findings as the source of truth.",
            ],
            "findings": [finding.__dict__ for finding in findings],
            "test_suggestions": [suggestion.__dict__ for suggestion in test_suggestions],
        }
