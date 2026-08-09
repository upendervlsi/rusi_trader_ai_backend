"""
========================================================================

RUSI Trader AI

MACD Feature Calculator

========================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from intelligence.core.feature_id import FeatureId
from intelligence.features.base_feature_calculator import BaseFeatureCalculator
from intelligence.features.ema.ema_calculator import EMACalculator
from intelligence.features.feature_definition import FeatureDefinition
from intelligence.features.macd.macd_result import MACDResult
from intelligence.models.feature_store import FeatureStore
from intelligence.models.feature_value import FeatureValue
from intelligence.models.market_series import MarketSeries


class MACDCalculator(BaseFeatureCalculator):
    """
    MACD Feature Calculator.
    """

    VERSION = "1.0"

    def __init__(self):

        self._ema12 = EMACalculator(period=12)
        self._ema26 = EMACalculator(period=26)
        self._ema9 = EMACalculator(period=9)

    @property
    def definition(self) -> FeatureDefinition:

        return FeatureDefinition(
            feature_id=FeatureId.MACD,
            name="MACD",
            category="Trend",
            description="Moving Average Convergence Divergence",
            version=self.VERSION,
        )

    def _calculate_macd_line(
        self,
        series: MarketSeries,
    ) -> List[float]:

        ema12 = self._ema12.calculate_series(series)
        ema26 = self._ema26.calculate_series(series)

        min_length = min(len(ema12), len(ema26))

        ema12 = ema12[-min_length:]
        ema26 = ema26[-min_length:]

        return [
            fast - slow
            for fast, slow in zip(ema12, ema26)
        ]

    def calculate_result(
        self,
        series: MarketSeries,
    ) -> MACDResult:

        macd_line = self._calculate_macd_line(series)

        signal_line = self._ema9.calculate_values(macd_line)

        min_length = min(
            len(macd_line),
            len(signal_line),
        )

        macd_line = macd_line[-min_length:]
        signal_line = signal_line[-min_length:]

        histogram = [
            macd - signal
            for macd, signal in zip(
                macd_line,
                signal_line,
            )
        ]

        return MACDResult(
            macd_line=macd_line,
            signal_line=signal_line,
            histogram=histogram,
        )

    def calculate(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> float:

        result = self.calculate_result(series)

        timestamp = (
            series.timestamps[-1]
            if series.timestamps
            else datetime.now()
        )

        feature_store.add(
            FeatureValue(
                feature_id=FeatureId.MACD,
                value=result.macd_line[-1],
                timestamp=timestamp,
                calculator="MACD",
                version=self.VERSION,
            )
        )

        feature_store.add(
            FeatureValue(
                feature_id=FeatureId.MACD_SIGNAL,
                value=result.signal_line[-1],
                timestamp=timestamp,
                calculator="MACD",
                version=self.VERSION,
            )
        )

        feature_store.add(
            FeatureValue(
                feature_id=FeatureId.MACD_HISTOGRAM,
                value=result.histogram[-1],
                timestamp=timestamp,
                calculator="MACD",
                version=self.VERSION,
            )
        )

        return result.macd_line[-1]
