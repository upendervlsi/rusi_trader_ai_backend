from common.enums import Trend


class TrendDetector:

    @staticmethod
    def detect(
            ema20,
            ema50,
            ema200):

        if ema20 > ema50 > ema200:
            return Trend.BULLISH

        if ema20 < ema50 < ema200:
            return Trend.BEARISH

        return Trend.SIDEWAYS
