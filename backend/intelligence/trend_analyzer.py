"""
============================================================

RUSI Trader AI

Trend Analyzer

Uses MarketSnapshot directly.

============================================================
"""

from .analyzer_result import AnalyzerResult


class TrendAnalyzer:

    @property
    def name(self) -> str:
        return "Trend"

    # ------------------------------------------------------
    # Analyze
    # ------------------------------------------------------

    def analyze(
        self,
        snapshot,
    ) -> AnalyzerResult:

        score = 0.0

        reasons = []

        metadata = {}

        # --------------------------------------------------
        # EMA
        # --------------------------------------------------

        metadata["ema20"] = snapshot.ema20
        metadata["ema50"] = snapshot.ema50

        if snapshot.ema20 > snapshot.ema50:

            score += 25

            reasons.append(
                "EMA20 is above EMA50."
            )

        else:

            score -= 25

            reasons.append(
                "EMA20 is below EMA50."
            )

        # --------------------------------------------------
        # SMA
        # --------------------------------------------------

        metadata["sma20"] = snapshot.sma20
        metadata["sma50"] = snapshot.sma50

        if snapshot.sma20 > snapshot.sma50:

            score += 20

            reasons.append(
                "SMA20 is above SMA50."
            )

        else:

            score -= 20

            reasons.append(
                "SMA20 is below SMA50."
            )

        # --------------------------------------------------
        # VWAP
        # --------------------------------------------------

        metadata["vwap"] = snapshot.vwap

        if snapshot.latest_close > snapshot.vwap:

            score += 15

            reasons.append(
                "Price is trading above VWAP."
            )

        else:

            score -= 15

            reasons.append(
                "Price is trading below VWAP."
            )

        # --------------------------------------------------
        # Market Structure
        # --------------------------------------------------

        metadata["market_structure"] = (
            snapshot.market_structure
        )

        if snapshot.market_structure == "BULLISH":

            score += 20

            reasons.append(
                "Market structure is bullish."
            )

        elif snapshot.market_structure == "BEARISH":

            score -= 20

            reasons.append(
                "Market structure is bearish."
            )

        else:

            reasons.append(
                "Market structure is neutral."
            )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if score >= 40:

            classification = "BULLISH"

        elif score <= -40:

            classification = "BEARISH"

        else:

            classification = "NEUTRAL"

        confidence = min(
            100.0,
            abs(score),
        )

        return AnalyzerResult(

            name=self.name,

            score=score,

            classification=classification,

            confidence=confidence,

            reasons=reasons,

            metadata=metadata,

        )
