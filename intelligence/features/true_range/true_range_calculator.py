"""
========================================================================

RUSI Trader AI

True Range Calculator

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


class TrueRangeCalculator(BaseFeatureCalculator):
    """
    Calculates True Range values.
    """

    @property
    def definition(self) -> FeatureDefinition:

        return FeatureDefinition(
            feature_id=FeatureId.TRUE_RANGE,
            name="True Range",
            category="Volatility",
            description="True Range",
            version="1.0",
        )

    def calculate(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> float:
        """
        Calculates the latest True Range.
        """

        tr_values = self.calculate_series(series)

        latest_tr = tr_values[-1]

        feature_store.add(
            FeatureValue(
                feature_id=FeatureId.TRUE_RANGE,
                value=latest_tr,
                timestamp=datetime.now(),
                calculator="TrueRange",
                version="1.0",
            )
        )

        return latest_tr

    def calculate_series(
        self,
        series: MarketSeries,
    ) -> List[float]:
        """
        Calculates True Range for every candle except the first.
        """

        if series.length < 2:
            raise ValueError(
                "True Range requires at least two candles."
            )

        tr_values: List[float] = []

        for i in range(1, series.length):

            high = series.high[i]
            low = series.low[i]
            previous_close = series.close[i - 1]

            tr = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )

            tr_values.append(tr)

        return tr_values
