"""
========================================================================

RUSI Trader AI

Market Regime Classifier

========================================================================
"""

from __future__ import annotations

from intelligence.market.market_regime import MarketRegime
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.core.feature_id import FeatureId


class MarketRegimeClassifier:

    def classify(
        self,
        context: EvidenceContext,
    ) -> MarketRegime:

        feature_store = context.feature_store

        price = feature_store.get_value(
            FeatureId.CLOSE_PRICE
        )

        ema = feature_store.get_value(
            FeatureId.EMA_20
        )

        atr = feature_store.get_value(
            FeatureId.ATR_14
        )

        volume = feature_store.get_value(
            FeatureId.VOLUME
        )

        avg_volume = feature_store.get_value(
            FeatureId.AVG_VOLUME_20
        )

        deviation = abs(price - ema) / ema

        volume_ratio = volume / avg_volume

        if atr < 1.0:

            return MarketRegime.LOW_VOLATILITY

        if deviation > 0.01 and volume_ratio > 1.20:

            return MarketRegime.TRENDING

        if deviation < 0.003:

            return MarketRegime.RANGING

        return MarketRegime.UNKNOWN
