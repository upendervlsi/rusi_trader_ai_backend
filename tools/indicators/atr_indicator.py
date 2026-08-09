"""
============================================================
RUSI Trader AI

ATR Indicator

Average True Range
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData


class ATRIndicator:
    """
    Average True Range (ATR)
    """

    def __init__(
        self,
        period: int = 14,
    ) -> None:

        if period <= 0:
            raise ValueError(
                "ATR period must be greater than zero."
            )

        self.period = period

    # ---------------------------------------------------------

    def calculate(
        self,
        market_data: MarketData,
    ) -> list[float]:

        candles = market_data.candles

        if len(candles) <= self.period:
            return []

        true_ranges: list[float] = []

        for index in range(1, len(candles)):

            current = candles[index]
            previous = candles[index - 1]

            tr = max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )

            true_ranges.append(tr)

        atr = (
            sum(true_ranges[: self.period])
            / self.period
        )

        values = [atr]

        for tr in true_ranges[self.period:]:

            atr = (
                (
                    atr
                    * (self.period - 1)
                )
                + tr
            ) / self.period

            values.append(atr)

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

        return f"ATR(period={self.period})"

    def __repr__(self) -> str:

        return self.__str__()
