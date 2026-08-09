"""
========================================================================

RUSI Trader AI

RSI Evidence Provider

Generates trading evidence using RSI.

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.evidence.evidence_provider import EvidenceProvider
from intelligence.models.feature_store import FeatureStore
from intelligence.signals.signal_type import SignalType


class RSIEvidenceProvider(EvidenceProvider):
    """
    RSI based evidence generator.
    """

    @property
    def name(self) -> str:
        return "RSI Evidence Provider"

    def generate(
        self,
        feature_store: FeatureStore,
        context: EvidenceContext,
    ) -> None:

        rsi = feature_store.try_get(
            FeatureId.RSI_14
        )

        if rsi is None:
            return

        value = rsi.value

        #
        # Oversold
        #

        if value <= 30.0:

            context.add(
                Evidence(
                    feature_id=FeatureId.RSI_14,
                    signal=SignalType.BUY,
                    confidence=80.0,
                    value=value,
                    reason="RSI indicates oversold condition",
                )
            )

        #
        # Overbought
        #

        elif value >= 70.0:

            context.add(
                Evidence(
                    feature_id=FeatureId.RSI_14,
                    signal=SignalType.SELL,
                    confidence=80.0,
                    value=value,
                    reason="RSI indicates overbought condition",
                )
            )

        #
        # Neutral
        #

        else:

            context.add(
                Evidence(
                    feature_id=FeatureId.RSI_14,
                    signal=SignalType.HOLD,
                    confidence=50.0,
                    value=value,
                    reason="RSI is in the neutral zone",
                )
            )
