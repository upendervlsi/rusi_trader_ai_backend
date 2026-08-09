"""
============================================================

Market Structure Engine

============================================================
"""

from intelligence.market_structure.market_structure_result import (
    MarketStructureResult,
)


class MarketStructureEngine:

    def analyze(self, snapshot):

        candles = snapshot.candles

        result = MarketStructureResult(
            reasons=[]
        )

        if len(candles) < 5:

            result.reasons.append(
                "Not enough candles."
            )

            return result

        last = candles[-1]
        prev = candles[-2]

        #
        # Simple V1 structure
        #

        if last.high > prev.high:

            result.higher_high = True

            result.reasons.append(
                "Higher High"
            )

        if last.low > prev.low:

            result.higher_low = True

            result.reasons.append(
                "Higher Low"
            )

        if last.high < prev.high:

            result.lower_high = True

            result.reasons.append(
                "Lower High"
            )

        if last.low < prev.low:

            result.lower_low = True

            result.reasons.append(
                "Lower Low"
            )

        #
        # Trend
        #

        if result.higher_high and result.higher_low:

            result.bullish_structure = True
            result.confidence = 75.0

        elif result.lower_high and result.lower_low:

            result.bearish_structure = True
            result.confidence = 75.0

        return result
