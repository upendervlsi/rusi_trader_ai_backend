"""
============================================================

RUSI Trader AI

Volume Analyzer

Analyzes volume participation and confirms
price movement using MarketSnapshot.

============================================================
"""

from .analyzer_result import AnalyzerResult


class VolumeAnalyzer:

    @property
    def name(self) -> str:
        return "Volume"

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

        #--------------------------------------------------
        # Current Volume
        #--------------------------------------------------

        current_volume = getattr(
            snapshot,
            "volume",
            0,
        )

        average_volume = getattr(
            snapshot,
            "average_volume",
            0,
        )

        delivery_percent = getattr(
            snapshot,
            "delivery_percent",
            0,
        )

        metadata["volume"] = current_volume
        metadata["average_volume"] = average_volume
        metadata["delivery_percent"] = delivery_percent

        #--------------------------------------------------
        # Relative Volume (RVOL)
        #--------------------------------------------------

        if average_volume > 0:

            rvol = current_volume / average_volume

        else:

            rvol = 0

        metadata["rvol"] = round(rvol, 2)

        if rvol >= 2.0:

            score += 30

            reasons.append(
                "Very high relative volume."
            )

        elif rvol >= 1.3:

            score += 20

            reasons.append(
                "Above-average trading volume."
            )

        else:

            reasons.append(
                "Normal trading volume."
            )

        #--------------------------------------------------
        # Delivery Percentage
        #--------------------------------------------------

        if delivery_percent >= 70:

            score += 25

            reasons.append(
                "Strong institutional delivery."
            )

        elif delivery_percent >= 50:

            score += 15

            reasons.append(
                "Healthy delivery participation."
            )

        #--------------------------------------------------
        # Volume Confirmation
        #--------------------------------------------------

        if (

            snapshot.latest_close >

            snapshot.vwap

            and

            rvol > 1.2

        ):

            score += 25

            reasons.append(
                "Price rise supported by volume."
            )

        elif (

            snapshot.latest_close <

            snapshot.vwap

            and

            rvol > 1.2

        ):

            score -= 15

            reasons.append(
                "Selling pressure confirmed."
            )

        #--------------------------------------------------
        # Classification
        #--------------------------------------------------

        if score >= 50:

            classification = "STRONG"

        elif score >= 20:

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
