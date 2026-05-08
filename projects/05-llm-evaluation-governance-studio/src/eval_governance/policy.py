from __future__ import annotations


class PolicyChecker:
    def check(
        self,
        text: str,
        requires_citation: bool,
        policy_tags: list[str],
    ) -> list[str]:
        violations = []
        normalized = text.lower()
        if requires_citation and "[source:" not in normalized:
            violations.append("missing-citation")
        if "unsafe-action" in policy_tags and "bypass" in normalized and "cannot recommend" not in normalized:
            violations.append("unsafe-bypass-recommendation")
        if "human-approval" in policy_tags and "approval" not in normalized and "review" not in normalized:
            violations.append("missing-human-approval")
        return violations
