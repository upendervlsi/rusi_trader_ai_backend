from typing import List


class EMACalculator:

    @staticmethod
    def calculate(prices: List[float], period: int):

        if len(prices) < period:
            return None

        multiplier = 2 / (period + 1)

        ema = sum(prices[:period]) / period

        for price in prices[period:]:

            ema = (price - ema) * multiplier + ema

        return round(ema, 2)
