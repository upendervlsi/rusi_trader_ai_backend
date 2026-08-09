"""
============================================================
RUSI Trader AI

SMA Indicator

Simple Moving Average
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData


class SMAIndicator:
    """
    Simple Moving Average Indicator.
    """

    def __init__(
        self,
        period: int = 20,
    ) -> None:

        if period <= 0:
            raise ValueError("SMA period must be greater than zero.")

        self.period = period

    # ---------------------------------------------------------

    def calculate(
        self,
        market_data: MarketData,
    ) -> list[float]:

        closes = [c.close for c in market_data.candles]

        if len(closes) < self.period:
            return []

        values: list[float] = []

        for i in range(self.period - 1, len(closes)):

            window = closes[i - self.period + 1 : i + 1]

            values.append(
                sum(window) / self.period
            )

        return values

    # ---------------------------------------------------------

    def latest(
        self,
        market_data: MarketData,
    ) -> float | None:

        values = self.calculate(market_data)

        if not values:
            return None

        return values[-1]

    # ---------------------------------------------------------

    def __str__(self) -> str:

        return f"SMA(period={self.period})"

    def __repr__(self) -> str:

        return self.__str__()
