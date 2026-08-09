"""
========================================================================

RUSI Trader AI

RSI Evidence Provider

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.evidence.base_evidence_provider import (
    BaseEvidenceProvider,
)
from intelligence.evidence.evidence import Evidence
from intelligence.models.feature_store import FeatureStore
from intelligence.signals.signal_type import SignalType


class RSIEvidenceProvider(BaseEvidenceProvider):
    """
    Generates trading evidence from RSI.
    """

    OVERSOLD = 30.0
    OVERBOUGHT = 70.0

    from intelligence.evidence.evidence_context import EvidenceContext

    def evaluate(
        self,
        context: EvidenceContext,
    ):

        rsi = context.feature_store.get_value(
            FeatureId.RSI_14
        )

        if rsi <= self.OVERSOLD:

            confidence = min(
                1.0,
                0.60 + (self.OVERSOLD - rsi) / 30.0,
            )

            return Evidence(
                feature_id=FeatureId.RSI_14,
                signal=SignalType.BUY,
                confidence=confidence,
                value=rsi,
                reason=(
                    f"RSI={rsi:.2f} indicates oversold conditions."
                ),
            )

        if rsi >= self.OVERBOUGHT:

            confidence = min(
                1.0,
                0.60 + (rsi - self.OVERBOUGHT) / 30.0,
            )

            return Evidence(
                feature_id=FeatureId.RSI_14,
                signal=SignalType.SELL,
                confidence=confidence,
                value=rsi,
                reason=(
                    f"RSI={rsi:.2f} indicates overbought conditions."
                ),
            )

        distance = min(
            abs(rsi - self.OVERSOLD),
            abs(self.OVERBOUGHT - rsi),
        )

        confidence = max(
            0.50,
            1.0 - distance / 40.0,
        )

        return Evidence(
            feature_id=FeatureId.RSI_14,
            signal=SignalType.HOLD,
            confidence=confidence,
            value=rsi,
            reason=(
                f"RSI={rsi:.2f} is within the neutral range."
            ),
        )
