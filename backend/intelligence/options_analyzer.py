"""
============================================================

RUSI Trader AI

Options Analyzer

Uses MarketSnapshot directly.

============================================================
"""

from .analyzer_result import AnalyzerResult


class OptionsAnalyzer:

    @property
    def name(self) -> str:
        return "Options"

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
        # PCR
        # --------------------------------------------------

        metadata["pcr"] = snapshot.pcr

        if 0.9 <= snapshot.pcr <= 1.3:

            score += 25

            reasons.append(
                "PCR indicates balanced bullish sentiment."
            )

        elif snapshot.pcr > 1.3:

            score += 15

            reasons.append(
                "PCR indicates strong bullish positioning."
            )

        else:

            score -= 20

            reasons.append(
                "PCR indicates bearish positioning."
            )

        # --------------------------------------------------
        # Open Interest
        # --------------------------------------------------

        metadata["open_interest"] = (
            snapshot.open_interest
        )

        if snapshot.open_interest > 0:

            score += 15

            reasons.append(
                "Open Interest data available."
            )

        # --------------------------------------------------
        # OI Change
        # --------------------------------------------------

        metadata["change_oi"] = (
            snapshot.change_oi
        )

        if snapshot.change_oi > 0:

            score += 20

            reasons.append(
                "Open Interest increasing."
            )

        elif snapshot.change_oi < 0:

            score -= 10

            reasons.append(
                "Open Interest decreasing."
            )

        # --------------------------------------------------
        # Implied Volatility
        # --------------------------------------------------

        metadata["implied_volatility"] = (
            snapshot.implied_volatility
        )

        if snapshot.implied_volatility < 20:

            score += 10

            reasons.append(
                "Implied Volatility is low."
            )

        elif snapshot.implied_volatility > 35:

            score -= 10

            reasons.append(
                "Implied Volatility is high."
            )

        # --------------------------------------------------
        # Max Pain
        # --------------------------------------------------

        metadata["max_pain"] = (
            snapshot.max_pain
        )

        reasons.append(
            f"Max Pain level : {snapshot.max_pain}"
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if score >= 50:

            classification = "BULLISH"

        elif score <= -20:

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
