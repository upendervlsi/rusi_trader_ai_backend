"""
========================================================================

RUSI Trader AI

Historical Data Engine

Responsible for maintaining historical MarketSeries.

========================================================================
"""

from __future__ import annotations

from intelligence.models.market_series import MarketSeries


class HistoricalDataEngine:
    """
    Stores and manages historical market data.
    """

    def __init__(self) -> None:

        self._series = MarketSeries()

    @property
    def series(self) -> MarketSeries:
        return self._series

    def append(
        self,
        timestamp,
        open_price,
        high,
        low,
        close,
        volume,
        open_interest=0.0,
    ) -> None:

        self._series.timestamps.append(timestamp)
        self._series.open.append(open_price)
        self._series.high.append(high)
        self._series.low.append(low)
        self._series.close.append(close)
        self._series.volume.append(volume)
        self._series.open_interest.append(open_interest)

    def clear(self) -> None:

        self._series = MarketSeries()

    def size(self) -> int:

        return self._series.length

    def validate(self) -> None:

        self._series.validate()
