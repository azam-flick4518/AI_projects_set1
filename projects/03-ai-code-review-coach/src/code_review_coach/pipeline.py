from __future__ import annotations

from code_review_coach.analyzer import CodeAnalyzer
from code_review_coach.models import ReviewReport
from code_review_coach.scanner import RepoScanner
from code_review_coach.synthesizer import DeterministicReviewSynthesizer, ReviewSynthesizer


class CodeReviewPipeline:
    def __init__(self, synthesizer: ReviewSynthesizer | None = None) -> None:
        self.scanner = RepoScanner()
        self.analyzer = CodeAnalyzer()
        self.synthesizer = synthesizer or DeterministicReviewSynthesizer()

    def review(self, repo_path: str) -> ReviewReport:
        files = self.scanner.scan(repo_path)
        findings, test_suggestions = self.analyzer.analyze(files)
        return self.synthesizer.synthesize(repo_path, findings, test_suggestions)
