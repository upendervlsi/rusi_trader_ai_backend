"""
============================================================

RUSI Trader AI

Confidence Engine

Combines analyzer outputs into one confidence score.

============================================================
"""

from typing import List

from .analyzer_result import AnalyzerResult


class ConfidenceEngine:

    """
    Calculates overall confidence from
    analyzer outputs.
    """

    DEFAULT_WEIGHTS = {

        "Trend": 0.30,

        "Momentum": 0.25,

        "Options": 0.25,

        "Volume": 0.20,

    }

    def __init__(
        self,
        weights=None,
    ):

        self.weights = (

            weights

            if weights is not None

            else self.DEFAULT_WEIGHTS

        )

    #------------------------------------------------------
    # Calculate
    #------------------------------------------------------

    def calculate(

        self,

        results: List[AnalyzerResult],

    ) -> dict:

        weighted_score = 0.0

        total_weight = 0.0

        reasons = []

        details = []

        for result in results:

            weight = self.weights.get(

                result.name,

                0.0,

            )

            total_weight += weight

            weighted_score += (

                result.score * weight

            )

            reasons.extend(

                result.reasons

            )

            details.append({

                "name":
                    result.name,

                "score":
                    result.score,

                "weight":
                    weight,

                "classification":
                    result.classification,

                "confidence":
                    result.confidence,

            })

        if total_weight > 0:

            weighted_score /= total_weight

        confidence = min(

            100.0,

            max(

                0.0,

                abs(weighted_score),

            ),

        )

        return {

            "confidence":

                confidence,

            "score":

                weighted_score,

            "details":

                details,

            "reasons":

                reasons,

        }
