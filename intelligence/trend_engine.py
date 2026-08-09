from intelligence.base_engine import BaseEngine
from common.engine_result import EngineResult
from common.trend_direction import TrendDirection


class TrendEngine(BaseEngine):

    MIN_REQUIRED_CANDLES = 20

    def verify(self, snapshot) -> bool:
        return len(snapshot.candles) >= self.MIN_REQUIRED_CANDLES

    def analyze(self, snapshot):
        ema20 = snapshot.indicators.ema20
        ema50 = snapshot.indicators.ema50

        latest = snapshot.latest_candle

        current_close = latest.close
        if not self.verify(snapshot):
            return EngineResult(
                engine_name="Trend Engine",
                signal=TrendDirection.SIDEWAYS.value,
                score=0.0,
                confidence=0.0,
                reasons=[
                    f"Minimum {self.MIN_REQUIRED_CANDLES} candles required."
                ],
            )

        previous = snapshot.candles[-2]
        current = snapshot.candles[-1]

        if current.close > previous.close:
            direction = TrendDirection.BULLISH

        elif current.close < previous.close:
            direction = TrendDirection.BEARISH

        else:
            direction = TrendDirection.SIDEWAYS

        confidence = abs(current.close - previous.close)

        return EngineResult(
            engine_name="Trend Engine",
            signal=direction.value,
            score=confidence,
            confidence=min(confidence, 100.0),
            reasons=[
                f"Previous Close : {previous.close}",
                f"Current Close  : {current.close}",
            ],
            details={
                "previous_close": previous.close,
                "current_close": current.close,
                "price_change": current.close - previous.close,
            },
        )
