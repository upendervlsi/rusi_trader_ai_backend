"""
========================================================================

RUSI Trader AI

EMA Feature Calculator

Calculates Exponential Moving Average.

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


class EMACalculator(BaseFeatureCalculator):
    """
    Generic EMA calculator.
    """

    def __init__(

        self,
        period: int,
        feature_id: FeatureId | None = None,
    ) -> None:
        self._period = period
        self._feature_id = feature_id

    def calculate_series(
        self,
        series: MarketSeries,
    ) -> List[float]:

        closes = series.close

        return self.calculate_values(closes)

    def calculate_values(
        self,
        values: List[float],
    ) -> List[float]:
        """
        Calculate EMA from a list of numeric values.
        """

        if len(values) < self._period:
            raise ValueError(
                f"EMA({self._period}) requires at least "
                f"{self._period} values."
            )

        ema_values: List[float] = []

        multiplier = 2 / (self._period + 1)

        first = (
            sum(values[: self._period])
            / self._period
        )

        ema_values.append(first)

        previous = first

        for value in values[self._period:]:

            ema = (
                (value - previous)
                * multiplier
            ) + previous

            ema_values.append(ema)

            previous = ema

        return ema_values

    @property
    def definition(self) -> FeatureDefinition:

        if self._feature_id is None:
            raise RuntimeError(
                "Internal EMA calculators do not expose a FeatureDefinition."
            )

        return FeatureDefinition(
            feature_id=self._feature_id,
            name=f"EMA {self._period}",
            category="Trend",
            description=f"{self._period} Period Exponential Moving Average",
            version="1.0",
        )
    def calculate(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> float:
        """
        Calculate the latest EMA from MarketSeries.
        """

        ema_values = self.calculate_series(series)

        latest = ema_values[-1]

        if self._feature_id is not None:

            feature_store.add(
                FeatureValue(
                    feature_id=self._feature_id,
                    value=latest,
                    timestamp=datetime.now(),
                    calculator=f"EMA({self._period})",
                    version="1.0",
                )
            )

        return latest
