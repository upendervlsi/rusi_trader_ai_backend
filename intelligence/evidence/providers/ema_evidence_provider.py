"""
========================================================================

RUSI Trader AI

EMA Evidence Provider

Generates trading evidence from EMA features.

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.evidence.evidence_provider import EvidenceProvider

from intelligence.core.feature_id import FeatureId
from intelligence.models.feature_store import FeatureStore
from intelligence.signals.signal_type import SignalType


class EMAEvidenceProvider(EvidenceProvider):
    """
    Generates BUY/SELL evidence using EMA20 and EMA50.
    """

    @property
    def name(self) -> str:
        return "EMA Evidence Provider"

    def generate(
        self,
        feature_store: FeatureStore,
        context: EvidenceContext,
    ) -> None:
        """
        Generate EMA evidence.
        """

        ema20 = feature_store.get(FeatureId.EMA_20)
        ema50 = feature_store.get(FeatureId.EMA_50)

        if ema20 is None or ema50 is None:
            return

        # ---------------------------------------------------------
        # Bullish
        # ---------------------------------------------------------

        if ema20.value > ema50.value:

            context.add(
                Evidence(
                    feature_id=FeatureId.EMA_20,
                    signal=SignalType.BUY,
                    confidence=70.0,
                    value=ema20.value,
                    reason="EMA20 is above EMA50",
                )
            )

        # ---------------------------------------------------------
        # Bearish
        # ---------------------------------------------------------

        elif ema20.value < ema50.value:

            context.add(
                Evidence(
                    feature_id=FeatureId.EMA_20,
                    signal=SignalType.SELL,
                    confidence=70.0,
                    value=ema20.value,
                    reason="EMA20 is below EMA50",
                )
            )

        # ---------------------------------------------------------
        # Neutral
        # ---------------------------------------------------------

        else:

            context.add(
                Evidence(
                    feature_id=FeatureId.EMA_20,
                    signal=SignalType.HOLD,
                    confidence=50.0,
                    value=ema20.value,
                    reason="EMA20 equals EMA50",
                )
            )
