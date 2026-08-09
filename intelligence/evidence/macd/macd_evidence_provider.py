"""
========================================================================

RUSI Trader AI

MACD Evidence Provider

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.evidence.base_evidence_provider import (
    BaseEvidenceProvider,
)
from intelligence.evidence.evidence import Evidence

from intelligence.signals.signal_type import SignalType
from intelligence.evidence.evidence_context import EvidenceContext

class MACDEvidenceProvider(BaseEvidenceProvider):
    """
    Generates evidence from MACD.
    """

    def evaluate(
        self,
        context: EvidenceContext,
    ) -> Evidence:

        if context.macd_result is None:

            raise ValueError(
                "MACDResult is required."
            )

        macd = context.macd_result.macd_line[-1]

        signal = context.macd_result.signal_line[-1]

        histogram = context.macd_result.histogram[-1]

        if histogram > 0:

            decision = SignalType.BUY

        elif histogram < 0:

            decision = SignalType.SELL

        else:

            decision = SignalType.HOLD

        confidence = min(
            1.0,
            0.60 + abs(histogram) / 2.0,
        )

        return Evidence(
            feature_id=FeatureId.MACD,
            signal=decision,
            confidence=confidence,
            value=histogram,
            reason=(
                f"MACD={macd:.4f}, "
                f"Signal={signal:.4f}, "
                f"Histogram={histogram:.4f}"
            ),
        )
