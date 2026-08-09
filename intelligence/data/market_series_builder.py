"""
========================================================================

RUSI Trader AI

Market Series Builder

Converts runtime Candle objects into MarketSeries.

========================================================================
"""

from __future__ import annotations

from intelligence.models.market_series import MarketSeries


class MarketSeriesBuilder:

    @staticmethod
    def build(candles) -> MarketSeries:

        series = MarketSeries()

        for candle in candles:

            series.timestamps.append(candle.timestamp)
            series.open.append(candle.open)
            series.high.append(candle.high)
            series.low.append(candle.low)
            series.close.append(candle.close)
            series.volume.append(candle.volume)

            if hasattr(candle, "open_interest"):
                series.open_interest.append(
                    candle.open_interest
                )
            else:
                series.open_interest.append(0.0)

        return series
