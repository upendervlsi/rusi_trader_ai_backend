"""
========================================================================

RUSI Trader AI

Feature Pipeline

========================================================================
"""

from __future__ import annotations

from trading.context.trading_context import TradingContext


class FeaturePipeline:

    def __init__(self, feature_store):

        self._feature_store = feature_store

    def execute(
        self,
        context: TradingContext,
    ) -> TradingContext:

        context.features = (
            self._feature_store.build(
                context.market_data,
                context.indicators,
            )
        )

        return context
