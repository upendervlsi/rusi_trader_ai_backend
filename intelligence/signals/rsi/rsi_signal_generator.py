"""
========================================================================

RUSI Trader AI

RSI Signal Generator

========================================================================
"""

from intelligence.core.feature_id import FeatureId
from intelligence.models.feature_store import FeatureStore
from intelligence.signals.base_signal_generator import BaseSignalGenerator
from intelligence.signals.signal_result import SignalResult
from intelligence.signals.signal_type import SignalType


class RSISignalGenerator(BaseSignalGenerator):

    def _generate(
        self,
        feature_store: FeatureStore,
    ) -> SignalResult:

        rsi = feature_store.get_value(
            FeatureId.RSI_14
        )

        if rsi < 30:

            return SignalResult(
                feature_id=FeatureId.RSI_14,
                signal=SignalType.BUY,
                confidence=0.90,
                reason="RSI indicates oversold conditions.",
            )

        if rsi > 70:

            return SignalResult(
                feature_id=FeatureId.RSI_14,
                signal=SignalType.SELL,
                confidence=0.90,
                reason="RSI indicates overbought conditions.",
            )

        return SignalResult(
            feature_id=FeatureId.RSI_14,
            signal=SignalType.HOLD,
            confidence=0.60,
            reason="RSI is in the neutral zone.",
        )
