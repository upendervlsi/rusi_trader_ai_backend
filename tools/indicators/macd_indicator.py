"""
============================================================
RUSI Trader AI

MACD Indicator

Moving Average Convergence Divergence
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData


class MACDIndicator:
    """
    MACD Indicator.
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> None:

        if fast_period <= 0:
            raise ValueError("fast_period must be > 0")

        if slow_period <= 0:
            raise ValueError("slow_period must be > 0")

        if signal_period <= 0:
            raise ValueError("signal_period must be > 0")

        if fast_period >= slow_period:
            raise ValueError(
                "fast_period must be smaller than slow_period"
            )

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    # ---------------------------------------------------------

    def _ema(
        self,
        values: list[float],
        period: int,
    ) -> list[float]:

        if len(values) < period:
            return []

        multiplier = 2.0 / (period + 1)

        ema = sum(values[:period]) / period

        result = [ema]

        for price in values[period:]:

            ema = (price - ema) * multiplier + ema

            result.append(ema)

        return result

    # ---------------------------------------------------------

    def calculate(
        self,
        market_data: MarketData,
    ) -> dict[str, list[float]]:

        closes = [c.close for c in market_data.candles]

        ema_fast = self._ema(closes, self.fast_period)
        ema_slow = self._ema(closes, self.slow_period)

        if not ema_fast or not ema_slow:
            return {
                "macd": [],
                "signal": [],
                "histogram": [],
            }

        offset = len(ema_fast) - len(ema_slow)

        ema_fast = ema_fast[offset:]

        macd = [
            f - s
            for f, s in zip(ema_fast, ema_slow)
        ]

        signal = self._ema(macd, self.signal_period)

        if not signal:
            return {
                "macd": macd,
                "signal": [],
                "histogram": [],
            }

        offset = len(macd) - len(signal)

        macd_tail = macd[offset:]

        histogram = [
            m - s
            for m, s in zip(macd_tail, signal)
        ]

        return {
            "macd": macd_tail,
            "signal": signal,
            "histogram": histogram,
        }

    # ---------------------------------------------------------

    def latest(
        self,
        market_data: MarketData,
    ) -> dict[str, float | None]:

        values = self.calculate(market_data)

        macd = values["macd"][-1] if values["macd"] else None
        signal = values["signal"][-1] if values["signal"] else None
        histogram = (
            values["histogram"][-1]
            if values["histogram"]
            else None
        )

        return {
            "macd": macd,
            "signal": signal,
            "histogram": histogram,
        }

    # ---------------------------------------------------------

    def __str__(self) -> str:

        return (
            f"MACD("
            f"{self.fast_period},"
            f"{self.slow_period},"
            f"{self.signal_period})"
        )

    def __repr__(self) -> str:

        return self.__str__()
