"""
========================================================================

RUSI Trader AI

RSI Calculator

Relative Strength Index using Wilder's Smoothing

========================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from intelligence.core.feature_id import FeatureId
from intelligence.features.base_feature_calculator import BaseFeatureCalculator
from intelligence.features.feature_definition import FeatureDefinition
from intelligence.features.gain_loss.gain_loss_calculator import (
    GainLossCalculator,
)
from intelligence.features.price_change.price_change_calculator import (
    PriceChangeCalculator,
)
from intelligence.math.wilder_smoothing import (
    WilderSmoothingCalculator,
)
from intelligence.models.feature_store import FeatureStore
from intelligence.models.feature_value import FeatureValue
from intelligence.models.market_series import MarketSeries


class RSICalculator(BaseFeatureCalculator):
    """
    Relative Strength Index using Wilder's smoothing.
    """

    def __init__(self, period: int = 14):

        self._period = period

        self._price_change = PriceChangeCalculator()

        self._gain_loss = GainLossCalculator()

        self._smoother = WilderSmoothingCalculator()

    @property
    def definition(self):

        return FeatureDefinition(
            feature_id=FeatureId.RSI_14,
            name="RSI",
            category="Momentum",
            description="Relative Strength Index",
            version="1.0",
        )

    def calculate_series(
        self,
        series: MarketSeries,
    ) -> List[float]:

        changes = self._price_change.calculate(series)

        gain_loss = self._gain_loss.calculate(changes)

        avg_gains = self._smoother.calculate(
            gain_loss.gains,
            self._period,
        )

        avg_losses = self._smoother.calculate(
            gain_loss.losses,
            self._period,
        )

        rsi_values: List[float] = []

        for avg_gain, avg_loss in zip(
            avg_gains,
            avg_losses,
        ):

            if avg_loss == 0:

                rsi = 100.0

            else:

                rs = avg_gain / avg_loss

                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        return rsi_values

    def calculate(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> float:

        values = self.calculate_series(series)

        latest = values[-1]

        feature_store.add(
            FeatureValue(
                feature_id=FeatureId.RSI_14,
                value=latest,
                timestamp=datetime.now(),
                calculator=f"RSI({self._period})",
                version="1.0",
            )
        )

        return latest
