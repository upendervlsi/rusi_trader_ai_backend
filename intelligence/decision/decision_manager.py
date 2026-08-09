"""
============================================================

RUSI Trader AI

Decision Manager

============================================================
"""

from __future__ import annotations

from intelligence.decision.decision import Decision
from intelligence.decision.decision_rule import DecisionRule
from intelligence.evidence.evidence_context import EvidenceContext


class DecisionManager:
    """
    Executes the configured decision rule(s).
    """

    def __init__(
        self,
        rule: DecisionRule,
    ) -> None:

        self._rule = rule

    @property
    def rule_name(self) -> str:
        return self._rule.name

    def evaluate(
        self,
        evidence: EvidenceContext,
    ) -> Decision:

        return self._rule.evaluate(
            evidence
        )
