"""
============================================================
RUSI Trader AI

ADX Indicator

Average Directional Index
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData


class ADXIndicator:
    """
    Average Directional Index
    """

    def __init__(
        self,
        period: int = 14,
    ) -> None:

        if period <= 0:
            raise ValueError(
                "ADX period must be greater than zero."
            )

        self.period = period

    # ---------------------------------------------------------

    def calculate(
        self,
        market_data: MarketData,
    ) -> list[float]:

        candles = market_data.candles

        if len(candles) <= self.period + 1:
            return []

        plus_dm = []
        minus_dm = []
        tr_list = []

        for i in range(1, len(candles)):

            current = candles[i]
            previous = candles[i - 1]

            up_move = current.high - previous.high
            down_move = previous.low - current.low

            pdm = up_move if (
                up_move > down_move and up_move > 0
            ) else 0.0

            mdm = down_move if (
                down_move > up_move and down_move > 0
            ) else 0.0

            tr = max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )

            plus_dm.append(pdm)
            minus_dm.append(mdm)
            tr_list.append(tr)

        adx_values = []

        tr14 = sum(tr_list[:self.period])
        plus14 = sum(plus_dm[:self.period])
        minus14 = sum(minus_dm[:self.period])

        for i in range(self.period, len(tr_list)):

            if i > self.period:

                tr14 = tr14 - (tr14 / self.period) + tr_list[i]
                plus14 = plus14 - (plus14 / self.period) + plus_dm[i]
                minus14 = minus14 - (minus14 / self.period) + minus_dm[i]

            if tr14 == 0:
                adx_values.append(0.0)
                continue

            plus_di = 100.0 * plus14 / tr14
            minus_di = 100.0 * minus14 / tr14

            denominator = plus_di + minus_di

            if denominator == 0:
                dx = 0.0
            else:
                dx = (
                    abs(plus_di - minus_di)
                    / denominator
                ) * 100.0

            adx_values.append(dx)

        return adx_values

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

        return f"ADX(period={self.period})"

    def __repr__(self) -> str:

        return self.__str__()
