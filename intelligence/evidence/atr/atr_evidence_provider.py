"""
========================================================================

RUSI Trader AI

ATR Evidence Provider

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.evidence.base_evidence_provider import BaseEvidenceProvider
from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.signals.signal_type import SignalType


class ATREvidenceProvider(BaseEvidenceProvider):

    ATR_THRESHOLD = 1.0

    def evaluate(
        self,
        context: EvidenceContext,
    ) -> Evidence:

        feature_store = context.feature_store

        atr = feature_store.get_value(
            FeatureId.ATR_14
        )

        if atr >= self.ATR_THRESHOLD:

            signal = SignalType.BUY

            confidence = min(
                1.0,
                0.60 + (atr / 10.0),
            )

            reason = (
                f"ATR={atr:.2f} "
                "High volatility"
            )

        else:

            signal = SignalType.HOLD

            confidence = 0.50

            reason = (
                f"ATR={atr:.2f} "
                "Low volatility"
            )

        return Evidence(
            feature_id=FeatureId.ATR_14,
            signal=signal,
            confidence=confidence,
            value=atr,
            reason=reason,
        )
