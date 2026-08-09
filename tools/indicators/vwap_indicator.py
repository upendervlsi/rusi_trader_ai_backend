"""
============================================================
RUSI Trader AI

VWAP Indicator

Volume Weighted Average Price
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData


class VWAPIndicator:
    """
    Volume Weighted Average Price
    """

    def calculate(
        self,
        market_data: MarketData,
    ) -> list[float]:

        candles = market_data.candles

        if not candles:
            return []

        cumulative_pv = 0.0
        cumulative_volume = 0.0

        values = []

        for candle in candles:

            typical_price = (
                candle.high
                + candle.low
                + candle.close
            ) / 3.0

            cumulative_pv += (
                typical_price
                * candle.volume
            )

            cumulative_volume += candle.volume

            if cumulative_volume == 0:

                values.append(0.0)

            else:

                values.append(
                    cumulative_pv
                    / cumulative_volume
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

    def __str__(self):

        return "VWAP()"

    def __repr__(self):

        return self.__str__()
