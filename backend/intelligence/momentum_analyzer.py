"""
============================================================

RUSI Trader AI

Momentum Analyzer

Uses MarketSnapshot directly.

============================================================
"""

from .analyzer_result import AnalyzerResult


class MomentumAnalyzer:

    @property
    def name(self) -> str:
        return "Momentum"

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
        # RSI
        # --------------------------------------------------

        metadata["rsi"] = snapshot.rsi

        if 50 <= snapshot.rsi <= 70:

            score += 25

            reasons.append(
                "RSI indicates healthy bullish momentum."
            )

        elif snapshot.rsi > 70:

            score -= 10

            reasons.append(
                "RSI indicates overbought condition."
            )

        else:

            score -= 15

            reasons.append(
                "RSI indicates weak momentum."
            )

        # --------------------------------------------------
        # MACD
        # --------------------------------------------------

        metadata["macd"] = snapshot.macd

        if snapshot.macd > 0:

            score += 25

            reasons.append(
                "MACD is bullish."
            )

        else:

            score -= 25

            reasons.append(
                "MACD is bearish."
            )

        # --------------------------------------------------
        # ADX
        # --------------------------------------------------

        metadata["adx"] = snapshot.adx

        if snapshot.adx >= 25:

            score += 20

            reasons.append(
                "ADX confirms strong trend."
            )

        else:

            reasons.append(
                "ADX indicates weak trend."
            )

        # --------------------------------------------------
        # ATR
        # --------------------------------------------------

        metadata["atr"] = snapshot.atr

        if snapshot.atr > 0:

            score += 10

            reasons.append(
                "ATR available for volatility calculation."
            )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if score >= 40:

            classification = "STRONG"

        elif score >= 15:

            classification = "MODERATE"

        else:

            classification = "WEAK"

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
