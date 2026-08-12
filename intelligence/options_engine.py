"""
============================================================

RUSI Trader AI

Runtime Options Intelligence Engine

============================================================
"""

from intelligence.base_engine import BaseEngine
from common.engine_result import EngineResult


class OptionsEngine(BaseEngine):
    """
    Runtime options intelligence.

    This engine consumes option analytics already published
    into snapshot.analysis.options.

    It never creates fake/default market values.
    """

    @property
    def name(self):
        return "Options Engine"

    def verify(self, snapshot) -> bool:
        analysis = getattr(snapshot, "analysis", None)

        if analysis is None:
            return False

        return getattr(
            analysis,
            "options",
            None,
        ) is not None

    def analyze(self, snapshot) -> EngineResult:
        analysis = getattr(snapshot, "analysis", None)

        option_data = (
            getattr(analysis, "options", None)
            if analysis is not None
            else None
        )

        if option_data is None:
            return EngineResult(
                engine_name=self.name,
                signal="NEUTRAL",
                score=0.0,
                confidence=0.0,
                reasons=[
                    "Options data is not available in the runtime snapshot."
                ],
                warnings=[
                    "Live option-chain analytics are not connected yet."
                ],
            )

        # Existing option analyzer result may expose
        # classification, score and confidence.
        classification = getattr(
            option_data,
            "classification",
            "NEUTRAL",
        )

        score = float(
            getattr(
                option_data,
                "score",
                0.0,
            )
        )

        confidence = float(
            getattr(
                option_data,
                "confidence",
                0.0,
            )
        )

        reasons = list(
            getattr(
                option_data,
                "reasons",
                [],
            )
        )

        metadata = getattr(
            option_data,
            "metadata",
            {}
        )

        return EngineResult(
            engine_name=self.name,
            signal=str(classification),
            score=score,
            confidence=confidence,
            reasons=reasons,
            details={
                "option_metadata": metadata,
            },
        )
