"""
============================================================
RUSI Trader AI

EMA Indicator

Exponential Moving Average
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData


class EMAIndicator:
    """
    Exponential Moving Average Indicator.
    """

    def __init__(
        self,
        period: int = 20,
    ) -> None:

        if period <= 0:
            raise ValueError("EMA period must be greater than zero.")

        self.period = period

    # ---------------------------------------------------------

    def calculate(
        self,
        market_data: MarketData,
    ) -> list[float]:

        closes = [c.close for c in market_data.candles]

        if len(closes) < self.period:
            return []

        multiplier = 2.0 / (self.period + 1)

        sma = sum(closes[: self.period]) / self.period

        ema_values = [sma]

        ema = sma

        for price in closes[self.period:]:

            ema = ((price - ema) * multiplier) + ema

            ema_values.append(ema)

        return ema_values

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

        return f"EMA(period={self.period})"

    def __repr__(self) -> str:

        return self.__str__()
