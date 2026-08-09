"""
============================================================

Simple Decision Rule

============================================================
"""

from __future__ import annotations

from intelligence.decision.decision import Decision
from intelligence.decision.decision_rule import DecisionRule
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.signals.signal_type import SignalType


class SimpleDecisionRule(DecisionRule):

    @property
    def name(self) -> str:
        return "Simple Decision Rule"

    def evaluate(
        self,
        evidence: EvidenceContext,
    ) -> Decision:

        score = 0.0
        reasons: list[str] = []

        for item in evidence.evidences:

            reasons.append(
                f"{item.feature_id.name} -> {item.signal.name}"
            )

            if item.signal == SignalType.BUY:
                score += item.confidence

            elif item.signal == SignalType.SELL:
                score -= item.confidence

        #
        # Decision Thresholds
        #

        if score >= 50.0:

            signal = SignalType.BUY

        elif score <= -50.0:

            signal = SignalType.SELL

        else:

            signal = SignalType.HOLD

        confidence = min(abs(score), 100.0)

        return Decision(
            signal=signal,
            confidence=confidence,
            score=score,
            reasons=reasons,
        )
