"""
============================================================

RUSI Trader AI

Recommendation Engine

Generates final trading recommendation.

============================================================
"""

from dataclasses import dataclass


@dataclass
class RecommendationResult:

    recommendation: str

    confidence: float

    score: float

    risk: str

    auto_trade: bool

    reasons: list[str]


class RecommendationEngine:

    """
    Converts confidence score into
    final trading recommendation.
    """

    BUY_THRESHOLD = 70

    SELL_THRESHOLD = -70

    AUTO_TRADE_THRESHOLD = 85

    def generate(
        self,
        confidence_result: dict,
    ) -> RecommendationResult:

        score = confidence_result["score"]

        confidence = confidence_result["confidence"]

        reasons = confidence_result["reasons"]

        #--------------------------------------------------
        # Recommendation
        #--------------------------------------------------

        if score >= self.BUY_THRESHOLD:

            recommendation = "BUY"

        elif score <= self.SELL_THRESHOLD:

            recommendation = "SELL"

        else:

            recommendation = "HOLD"

        #--------------------------------------------------
        # Risk
        #--------------------------------------------------

        if confidence >= 85:

            risk = "LOW"

        elif confidence >= 60:

            risk = "MEDIUM"

        else:

            risk = "HIGH"

        #--------------------------------------------------
        # Auto Trade
        #--------------------------------------------------

        auto_trade = (

            recommendation != "HOLD"

            and

            confidence >= self.AUTO_TRADE_THRESHOLD

        )

        return RecommendationResult(

            recommendation=recommendation,

            confidence=confidence,

            score=score,

            risk=risk,

            auto_trade=auto_trade,

            reasons=reasons,

        )
