"""
========================================================================

RUSI Trader AI

ATR Calculator

Average True Range using Wilder's Smoothing

========================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from intelligence.core.feature_id import FeatureId
from intelligence.features.base_feature_calculator import BaseFeatureCalculator
from intelligence.features.feature_definition import FeatureDefinition
from intelligence.features.true_range.true_range_calculator import (
    TrueRangeCalculator,
)
from intelligence.models.feature_store import FeatureStore
from intelligence.models.feature_value import FeatureValue
from intelligence.models.market_series import MarketSeries
from intelligence.math.wilder_smoothing import (
    WilderSmoothingCalculator,
)

class ATRCalculator(BaseFeatureCalculator):
    """
    Average True Range using Wilder's smoothing.
    """

    def __init__(self, period: int = 14):

        self._period = period
        self._tr = TrueRangeCalculator()
        self._smoother = WilderSmoothingCalculator()

    @property
    def definition(self):

        return FeatureDefinition(
            feature_id=FeatureId.ATR_14,
            name="ATR",
            category="Volatility",
            description="Average True Range",
            version="1.0",
        )

    def calculate_series(
        self,
        series: MarketSeries,
    ) -> List[float]:

        tr_values = self._tr.calculate_series(series)

        return self._smoother.calculate(
            values=tr_values,
            period=self._period,
        )

    def calculate(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> float:

        atr_values = self.calculate_series(series)

        latest = atr_values[-1]

        feature_store.add(
            FeatureValue(
                feature_id=FeatureId.ATR_14,
                value=latest,
                timestamp=datetime.now(),
                calculator=f"ATR({self._period})",
                version="1.0",
            )
        )

        return latest
