"""
============================================================

rusi_trader_ai

Trend Engine

------------------------------------------------------------

This engine is responsible for:

1. Calculating EMA values
2. Detecting trend direction
3. Calculating trend strength
4. Generating explanation
5. Returning EngineResult

============================================================
"""

from intelligence.base_engine import BaseEngine

from intelligence.trend.ema_calculator import EMACalculator
from intelligence.trend.trend_detector import TrendDetector
from intelligence.trend.trend_strength import TrendStrength
from intelligence.trend.trend_explainer import TrendExplainer

from common.enums import Recommendation
from common.models import EngineResult


class TrendEngine(BaseEngine):

    def verify(self, snapshot):
        """
        Basic verification for Sprint-2.
        More checks will be added later.
        """
        return snapshot is not None

    def analyze(self, snapshot):

        if not self.verify(snapshot):
            raise ValueError("Invalid Market Snapshot")

        #
        # Temporary historical prices.
        #
        # Sprint-3 will replace this with
        # actual Angel One historical candles.
        #

        prices = [snapshot.close_price] * 250

        ema20 = EMACalculator.calculate(prices, 20)
        ema50 = EMACalculator.calculate(prices, 50)
        ema200 = EMACalculator.calculate(prices, 200)

        trend = TrendDetector.detect(
            ema20,
            ema50,
            ema200
        )

        strength = TrendStrength.calculate(
            ema20,
            ema50,
            ema200
        )

        explanations = TrendExplainer.explain(trend)

        if trend.value == "Bullish":
            recommendation = Recommendation.BUY
            buy_score = 12
            sell_score = 0
            wait_score = 0

        elif trend.value == "Bearish":
            recommendation = Recommendation.SELL
            buy_score = 0
            sell_score = 12
            wait_score = 0

        else:
            recommendation = Recommendation.WAIT
            buy_score = 0
            sell_score = 0
            wait_score = 10

        print()
        print("=" * 60)
        print("Trend Engine")
        print("=" * 60)

        print(f"Symbol      : {snapshot.symbol}")
        print(f"Price       : {snapshot.close_price}")

        print()

        print(f"EMA20       : {ema20}")
        print(f"EMA50       : {ema50}")
        print(f"EMA200      : {ema200}")

        print()

        print(f"Trend       : {trend.value}")
        print(f"Strength    : {strength:.2f}")

        print()

        print("Explanation")

        for item in explanations:
            print(f"  ✓ {item}")

        print()

        return EngineResult(

            engine_name="Trend Engine",

            recommendation=recommendation,

            confidence=strength,

            buy_score=buy_score,

            sell_score=sell_score,

            wait_score=wait_score,

            verified=True,

            reason=explanations[0],

            learning_notes=explanations

        )

    def explain(self):
        return "Trend Engine"
