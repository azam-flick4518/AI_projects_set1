from __future__ import annotations

from eval_governance.models import CaseResult, EvalCase, EvalReport
from eval_governance.policy import PolicyChecker
from eval_governance.providers import FixtureModelProvider, ModelProvider


class Evaluator:
    def __init__(self, provider: ModelProvider | None = None, policy_checker: PolicyChecker | None = None) -> None:
        self.provider = provider or FixtureModelProvider()
        self.policy_checker = policy_checker or PolicyChecker()

    def run(self, cases: list[EvalCase]) -> EvalReport:
        results = [self._evaluate_case(eval_case) for eval_case in cases]
        passed = sum(1 for result in results if result.passed)
        average = sum(result.score for result in results) / len(results) if results else 0.0
        return EvalReport(
            total_cases=len(results),
            passed_cases=passed,
            average_score=round(average, 3),
            results=results,
            assumptions=[
                "The local provider returns deterministic fixture outputs.",
                "Expected and forbidden checks use case-insensitive substring matching.",
                "Production runs can swap in LLMProvider while keeping the same governance checks.",
            ],
        )

    def _evaluate_case(self, eval_case: EvalCase) -> CaseResult:
        output = self.provider.generate(eval_case)
        normalized = output.text.lower()
        missing = [item for item in eval_case.expected_contains if item.lower() not in normalized]
        forbidden = [item for item in eval_case.forbidden_contains if item.lower() in normalized]
        policy_violations = self.policy_checker.check(
            output.text,
            eval_case.requires_citation,
            eval_case.policy_tags,
        )
        expected_score = (
            (len(eval_case.expected_contains) - len(missing)) / len(eval_case.expected_contains)
            if eval_case.expected_contains
            else 1.0
        )
        penalty = 0.25 * (len(forbidden) + len(policy_violations))
        score = round(max(0.0, expected_score - penalty), 3)
        passed = not missing and not forbidden and not policy_violations
        return CaseResult(
            case_id=eval_case.id,
            passed=passed,
            score=score,
            missing_expected=missing,
            forbidden_found=forbidden,
            policy_violations=policy_violations,
            output=output.text,
        )
