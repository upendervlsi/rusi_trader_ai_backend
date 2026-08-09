"""
========================================================================

RUSI Trader AI

Volume Evidence Provider

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


class VolumeEvidenceProvider(BaseEvidenceProvider):

    HIGH_VOLUME_RATIO = 1.20

    LOW_VOLUME_RATIO = 0.80

    def evaluate(
        self,
        context: EvidenceContext,
    ) -> Evidence:

        feature_store = context.feature_store

        volume = feature_store.get_value(
            FeatureId.VOLUME
        )

        average_volume = feature_store.get_value(
            FeatureId.AVG_VOLUME_20
        )

        ratio = volume / average_volume

        if ratio >= self.HIGH_VOLUME_RATIO:

            signal = SignalType.BUY

            confidence = min(
                1.0,
                0.60 + (ratio - 1.0),
            )

            reason = (
                f"Volume={volume:.0f}, "
                f"Avg20={average_volume:.0f}, "
                f"Ratio={ratio:.2f}"
            )

        elif ratio <= self.LOW_VOLUME_RATIO:

            signal = SignalType.HOLD

            confidence = 0.50

            reason = (
                f"Volume={volume:.0f}, "
                f"Avg20={average_volume:.0f}, "
                f"Ratio={ratio:.2f}"
            )

        else:

            signal = SignalType.HOLD

            confidence = 0.60

            reason = (
                f"Volume Normal "
                f"Ratio={ratio:.2f}"
            )

        return Evidence(
            feature_id=FeatureId.VOLUME,
            signal=signal,
            confidence=confidence,
            value=ratio,
            reason=reason,
        )
