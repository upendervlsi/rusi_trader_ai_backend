"""
============================================================

RUSI Trader AI

Risk Engine

============================================================
"""

from trading.decision.decision_result import (
    DecisionResult,
)

from trading.risk.risk_result import (
    RiskResult,
)


class RiskEngine:
    """
    Validates whether a trade is allowed.
    """

    MIN_CONFIDENCE = 65.0

    DEFAULT_RR = 2.0

    DEFAULT_POSITION_SIZE = 1

    def evaluate(
        self,
        decision: DecisionResult,
    ) -> RiskResult:

        result = RiskResult()

        if decision.is_hold():

            result.reject(
                "Decision is HOLD."
            )

            return result

        if decision.confidence < self.MIN_CONFIDENCE:

            result.reject(
                "Confidence below threshold."
            )

            return result

        result.approve()

        result.position_size = (
            self.DEFAULT_POSITION_SIZE
        )

        result.risk_score = (
            decision.confidence
        )

        result.risk_reward_ratio = (
            self.DEFAULT_RR
        )

        result.reasons.append(
            "Confidence validated."
        )

        return result
