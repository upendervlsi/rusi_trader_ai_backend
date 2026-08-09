"""
============================================================
RUSI Trader AI

RSI Indicator

Relative Strength Index
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData


class RSIIndicator:
    """
    Relative Strength Index (RSI) using Wilder's smoothing.
    """

    def __init__(
        self,
        period: int = 14,
    ) -> None:

        if period <= 0:
            raise ValueError("RSI period must be greater than zero.")

        self.period = period

    # ---------------------------------------------------------

    def calculate(
        self,
        market_data: MarketData,
    ) -> list[float]:

        closes = [c.close for c in market_data.candles]

        if len(closes) <= self.period:
            return []

        gains: list[float] = []
        losses: list[float] = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i - 1]

            gains.append(max(change, 0.0))
            losses.append(max(-change, 0.0))

        avg_gain = sum(gains[: self.period]) / self.period
        avg_loss = sum(losses[: self.period]) / self.period

        values: list[float] = []

        if avg_loss == 0:
            values.append(100.0)
        else:
            rs = avg_gain / avg_loss
            values.append(100.0 - (100.0 / (1.0 + rs)))

        for i in range(self.period, len(gains)):

            avg_gain = (
                (avg_gain * (self.period - 1)) + gains[i]
            ) / self.period

            avg_loss = (
                (avg_loss * (self.period - 1)) + losses[i]
            ) / self.period

            if avg_loss == 0:
                values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                values.append(
                    100.0 - (100.0 / (1.0 + rs))
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

        return f"RSI(period={self.period})"

    def __repr__(self) -> str:

        return self.__str__()
