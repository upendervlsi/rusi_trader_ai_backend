"""
============================================================

Simple Moving Average

============================================================
"""


from indicators.base_indicator import BaseIndicator


class SMAIndicator(BaseIndicator):

    def calculate(self, candles, period=20):

        if len(candles) < period:
            return None

        closes = []

        for candle in candles[-period:]:
            closes.append(candle.close)

        return sum(closes) / len(closes)
