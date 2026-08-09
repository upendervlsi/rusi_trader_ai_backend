"""
========================================================================

RUSI Trader AI

EMA Evidence Provider

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.evidence.base_evidence_provider import (
    BaseEvidenceProvider,
)
from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import (
    EvidenceContext,
)
from intelligence.signals.signal_type import SignalType


class EMAEvidenceProvider(BaseEvidenceProvider):
    """
    Generates trend evidence using the EMA.

    Assumption:
        FeatureStore contains:

            FeatureId.CLOSE_PRICE
            FeatureId.EMA_20
    """

    TREND_THRESHOLD = 0.002      # 0.20%

    def evaluate(
        self,
        context: EvidenceContext,
    ) -> Evidence:

        feature_store = context.feature_store

        price = feature_store.get_value(
            FeatureId.CLOSE_PRICE
        )

        ema = feature_store.get_value(
            FeatureId.EMA_20
        )

        deviation = (price - ema) / ema

        if deviation > self.TREND_THRESHOLD:

            signal = SignalType.BUY

        elif deviation < -self.TREND_THRESHOLD:

            signal = SignalType.SELL

        else:

            signal = SignalType.HOLD

        confidence = min(
            1.0,
            0.60 + abs(deviation) * 20.0,
        )

        return Evidence(
            feature_id=FeatureId.EMA_20,
            signal=signal,
            confidence=confidence,
            value=deviation,
            reason=(
                f"Price={price:.2f}, "
                f"EMA20={ema:.2f}, "
                f"Deviation={deviation:.4%}"
            ),
        )
