"""
========================================================================

RUSI Trader AI

SMA Feature Calculator

Calculates Simple Moving Average.

========================================================================
"""

from __future__ import annotations

from datetime import datetime

from intelligence.core.feature_id import FeatureId
from intelligence.features.base_feature_calculator import BaseFeatureCalculator
from intelligence.features.feature_definition import FeatureDefinition
from intelligence.models.feature_store import FeatureStore
from intelligence.models.feature_value import FeatureValue
from intelligence.models.market_series import MarketSeries


class SMACalculator(BaseFeatureCalculator):
    """
    Generic SMA calculator.
    """

    def __init__(
        self,
        period: int,
        feature_id: FeatureId,
    ) -> None:

        self._period = period
        self._feature_id = feature_id

    @property
    def definition(self) -> FeatureDefinition:

        return FeatureDefinition(
            feature_id=self._feature_id,
            name=f"SMA {self._period}",
            category="Trend",
            description=f"{self._period} Period Simple Moving Average",
            version="1.0",
        )

    def calculate(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> float:

        closes = series.close

        if len(closes) < self._period:
            raise ValueError(
                f"SMA({self._period}) requires at least {self._period} candles."
            )

        sma = sum(closes[-self._period:]) / self._period

        feature_store.add(
            FeatureValue(
                feature_id=self._feature_id,
                value=sma,
                timestamp=datetime.now(),
                calculator=f"SMA({self._period})",
                version="1.0",
            )
        )

        return sma
