"""
========================================================================

RUSI Trader AI

Price Change Feature Calculator

========================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from intelligence.core.feature_id import FeatureId
from intelligence.features.base_feature_calculator import BaseFeatureCalculator
from intelligence.features.feature_definition import FeatureDefinition
from intelligence.models.feature_store import FeatureStore
from intelligence.models.feature_value import FeatureValue
from intelligence.models.market_series import MarketSeries


class PriceChangeCalculator:
    """
    Computes close-to-close price changes.
    """

    VERSION = "1.0"
    def calculate(
        self,
        series: MarketSeries,
    ) -> List[float]:

        if series.length < 2:
            raise ValueError(
                "Price changes require at least two candles."
            )

        changes = []

        for i in range(1, series.length):

            changes.append(
                series.close[i] - series.close[i - 1]
            )

        return changes
    @property
    def definition(self) -> FeatureDefinition:

        return FeatureDefinition(
            feature_id=FeatureId.PRICE_CHANGE,
            name="Price Change",
            category="Price",
            description="Close-to-close price change",
            version=self.VERSION,
        )

    def calculate_changes(
        self,
        series: MarketSeries,
    ) -> List[float]:
        """
        Returns:
            Close[i] - Close[i-1]
        """

        if series.length < 2:
            raise ValueError(
                "Price changes require at least two candles."
            )

        changes: List[float] = []

        for i in range(1, series.length):
            changes.append(
                series.close[i] - series.close[i - 1]
            )

        return changes
