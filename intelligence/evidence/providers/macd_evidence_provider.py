"""
========================================================================

RUSI Trader AI

MACD Evidence Provider

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.evidence.evidence_provider import EvidenceProvider
from intelligence.models.feature_store import FeatureStore
from intelligence.signals.signal_type import SignalType


class MACDEvidenceProvider(EvidenceProvider):

    @property
    def name(self) -> str:
        return "MACD Evidence Provider"

    def generate(
        self,
        feature_store: FeatureStore,
        context: EvidenceContext,
    ) -> None:

        macd = feature_store.try_get(
            FeatureId.MACD
        )

        signal = feature_store.try_get(
            FeatureId.MACD_SIGNAL
        )

        if macd is None or signal is None:
            return

        if macd.value > signal.value:

            context.add(
                Evidence(
                    feature_id=FeatureId.MACD,
                    signal=SignalType.BUY,
                    confidence=75.0,
                    value=macd.value,
                    reason="MACD crossed above signal",
                )
            )

        elif macd.value < signal.value:

            context.add(
                Evidence(
                    feature_id=FeatureId.MACD,
                    signal=SignalType.SELL,
                    confidence=75.0,
                    value=macd.value,
                    reason="MACD crossed below signal",
                )
            )

        else:

            context.add(
                Evidence(
                    feature_id=FeatureId.MACD,
                    signal=SignalType.HOLD,
                    confidence=50.0,
                    value=macd.value,
                    reason="MACD equals signal",
                )
            )
