"""
============================================================

RUSI Trader AI

Decision Engine

============================================================
"""

from common.analysis.evidence_bundle import EvidenceBundle

from trading.decision.decision_result import (
    DecisionResult,
)

from trading.decision.trading_action import (
    TradingAction,
)


class DecisionEngine:
    """
    Converts trading evidence into a trading decision.
    """

    STRONG_BUY = 80.0
    BUY = 65.0

    STRONG_SELL = 80.0
    SELL = 65.0

    HOLD_MARGIN = 10.0

    MIN_CONFIDENCE = 65.0

    def evaluate(
        self,
        evidence: EvidenceBundle,
    ) -> DecisionResult:

        result = DecisionResult()

        result.bullish_score = (
            evidence.bullish_score
        )

        result.bearish_score = (
            evidence.bearish_score
        )

        result.confidence = (
            evidence.confidence_score
        )

        result.probability = max(
            evidence.bullish_score,
            evidence.bearish_score,
        )

        result.explanation.extend(
            evidence.bullish_reasons
        )

        result.explanation.extend(
            evidence.bearish_reasons
        )

        bullish = evidence.bullish_score
        bearish = evidence.bearish_score
        confidence = evidence.confidence_score

        # HOLD when evidence is too close
        if abs(bullish - bearish) <= self.HOLD_MARGIN:
            result.action = TradingAction.HOLD
            result.explanation.append(
                "Bullish and bearish evidence are balanced."
            )
            return result

        # BUY
        if (
            bullish >= self.BUY
            and confidence >= self.MIN_CONFIDENCE
            and bullish > bearish
        ):
            result.action = TradingAction.BUY
            return result

        # SELL
        if (
            bearish >= self.SELL
            and confidence >= self.MIN_CONFIDENCE
            and bearish > bullish
        ):
            result.action = TradingAction.SELL
            return result

        result.action = TradingAction.HOLD

        return result
