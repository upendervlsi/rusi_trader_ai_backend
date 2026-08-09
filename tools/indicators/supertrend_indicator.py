"""
============================================================
RUSI Trader AI

SuperTrend Indicator
============================================================
"""

from __future__ import annotations

from tools.indicators.atr_indicator import ATRIndicator
from tools.scanner.market_data_models import MarketData


class SuperTrendIndicator:
    """
    SuperTrend Indicator
    """

    def __init__(
        self,
        period: int = 10,
        multiplier: float = 3.0,
    ) -> None:

        if period <= 0:
            raise ValueError(
                "Period must be greater than zero."
            )

        if multiplier <= 0:
            raise ValueError(
                "Multiplier must be greater than zero."
            )

        self.period = period
        self.multiplier = multiplier
        self._atr = ATRIndicator(period)

    # ---------------------------------------------------------

    def calculate(
        self,
        market_data: MarketData,
    ) -> list[dict[str, object]]:

        candles = market_data.candles
        atr_values = self._atr.calculate(market_data)

        if not atr_values:
            return []

        results = []

        start = len(candles) - len(atr_values)

        trend = "UP"

        for index, atr in enumerate(atr_values):

            candle = candles[start + index]

            hl2 = (
                candle.high + candle.low
            ) / 2.0

            upper = hl2 + (
                self.multiplier * atr
            )

            lower = hl2 - (
                self.multiplier * atr
            )

            if candle.close >= hl2:
                trend = "UP"
                value = lower
            else:
                trend = "DOWN"
                value = upper

            results.append(
                {
                    "value": value,
                    "trend": trend,
                }
            )

        return results

    # ---------------------------------------------------------

    def latest(
        self,
        market_data: MarketData,
    ) -> dict[str, object] | None:

        values = self.calculate(market_data)

        if not values:
            return None

        return values[-1]

    # ---------------------------------------------------------

    def __str__(self):

        return (
            f"SuperTrend("
            f"period={self.period},"
            f"multiplier={self.multiplier})"
        )

    def __repr__(self):

        return self.__str__()
