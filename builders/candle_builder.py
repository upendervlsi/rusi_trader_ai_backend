"""
============================================================

Candle Builder

Converts broker candle responses into
internal Candle objects.

============================================================
"""

from datetime import datetime

from common.candle import Candle


class CandleBuilder:

    @staticmethod
    def build(raw_candles):

        candles = []

        if raw_candles is None:
            return candles

        for row in raw_candles:

            candles.append(

                Candle(

                    timestamp=datetime.fromisoformat(row[0]),

                    open=float(row[1]),

                    high=float(row[2]),

                    low=float(row[3]),

                    close=float(row[4]),

                    volume=int(row[5]),
                )

            )

        return candles
