from __future__ import annotations

import ast
import re

from code_review_coach.models import Finding, SourceFile, TestSuggestion


SECRET_PATTERN = re.compile(r"(api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE)


class CodeAnalyzer:
    def analyze(self, files: list[SourceFile]) -> tuple[list[Finding], list[TestSuggestion]]:
        findings: list[Finding] = []
        tests: list[TestSuggestion] = []
        for source in files:
            findings.extend(self._scan_text(source))
            findings.extend(self._scan_ast(source))
            tests.extend(self._suggest_tests(source))
        return findings, tests

    def _scan_text(self, source: SourceFile) -> list[Finding]:
        findings = []
        for line_number, line in enumerate(source.text.splitlines(), start=1):
            if SECRET_PATTERN.search(line):
                findings.append(
                    Finding(
                        rule_id="security-hardcoded-secret",
                        title="Hardcoded secret",
                        severity="high",
                        path=source.path,
                        line=line_number,
                        message="A credential-like value appears to be hardcoded.",
                        recommendation="Load secrets from environment or a secret manager.",
                    )
                )
            if "TODO" in line:
                findings.append(
                    Finding(
                        rule_id="maintainability-todo",
                        title="Unresolved TODO",
                        severity="low",
                        path=source.path,
                        line=line_number,
                        message="A TODO remains in executable code.",
                        recommendation="Convert the TODO into a tracked task or implement it before merge.",
                    )
                )
        return findings

    def _scan_ast(self, source: SourceFile) -> list[Finding]:
        findings = []
        try:
            tree = ast.parse(source.text)
        except SyntaxError as exc:
            return [
                Finding(
                    rule_id="correctness-syntax-error",
                    title="Syntax error",
                    severity="high",
                    path=source.path,
                    line=exc.lineno or 1,
                    message=exc.msg,
                    recommendation="Fix syntax before review.",
                )
            ]

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append(
                    Finding(
                        rule_id="reliability-broad-except",
                        title="Broad exception handler",
                        severity="medium",
                        path=source.path,
                        line=node.lineno,
                        message="Bare except can hide operational failures.",
                        recommendation="Catch specific exceptions and preserve error context.",
                    )
                )
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                findings.append(
                    Finding(
                        rule_id="security-dynamic-execution",
                        title="Dynamic code execution",
                        severity="high",
                        path=source.path,
                        line=node.lineno,
                        message=f"`{node.func.id}` executes dynamic code.",
                        recommendation="Replace dynamic execution with explicit parsing or dispatch.",
                    )
                )
        return findings

    def _suggest_tests(self, source: SourceFile) -> list[TestSuggestion]:
        suggestions = []
        if "payment" in source.text.lower():
            suggestions.append(
                TestSuggestion(
                    path=source.path,
                    scenario="Add negative tests for failed payment authorization and token validation.",
                    reason="Payment paths are customer-impacting and high risk.",
                )
            )
        if "except" in source.text:
            suggestions.append(
                TestSuggestion(
                    path=source.path,
                    scenario="Add tests that assert exception handling preserves error context.",
                    reason="Exception paths are easy to regress silently.",
                )
            )
        return suggestions
