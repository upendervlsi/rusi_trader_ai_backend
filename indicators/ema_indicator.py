"""
============================================================

Exponential Moving Average

============================================================
"""

from indicators.base_indicator import BaseIndicator


class EMAIndicator(BaseIndicator):

    def calculate(self, candles, period=20):

        if len(candles) < period:
            return None

        closes = [c.close for c in candles]

        multiplier = 2 / (period + 1)

        ema = sum(closes[:period]) / period

        for price in closes[period:]:

            ema = ((price - ema) * multiplier) + ema

        return ema
