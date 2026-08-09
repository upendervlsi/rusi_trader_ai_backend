"""
============================================================
RUSI Trader AI

Unit Tests

Decision Engine
============================================================
"""

from tools.decision.decision_engine import DecisionEngine
from tools.decision.decision_models import (
    TradeSignal,
    SignalStrength,
)
from tools.scanner.market_data_models import (
    Candle,
    MarketData,
)


class TestDecisionEngine:

    def setup_method(self):

        candles = []

        price = 100.0

        for _ in range(40):

            candles.append(
                Candle(
                    timestamp="2026-01-01",
                    open=price,
                    high=price + 2.0,
                    low=price - 2.0,
                    close=price + 1.0,
                    volume=1000,
                )
            )

            price += 1.0

        self.market_data = MarketData(
            symbol="TEST",
            exchange="NSE",
            timeframe="1D",
            candles=candles,
        )

        self.engine = DecisionEngine()

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.engine is not None

    # ---------------------------------------------------------

    def test_evaluate(self):

        result = self.engine.evaluate(
            self.market_data
        )

        assert result.symbol == "TEST"

        assert result.signal in (
            TradeSignal.BUY,
            TradeSignal.SELL,
            TradeSignal.HOLD,
        )

        assert isinstance(
            result.confidence,
            float,
        )

        assert result.strength in (
            SignalStrength.VERY_WEAK,
            SignalStrength.WEAK,
            SignalStrength.MEDIUM,
            SignalStrength.STRONG,
            SignalStrength.VERY_STRONG,
        )

    # ---------------------------------------------------------

    def test_indicator_snapshot(self):

        result = self.engine.evaluate(
            self.market_data
        )

        assert result.indicators is not None

        assert len(
            result.indicators.values
        ) > 0

    # ---------------------------------------------------------

    def test_reasons(self):

        result = self.engine.evaluate(
            self.market_data
        )

        assert isinstance(
            result.reasons,
            list,
        )

        assert len(result.reasons) >= 1

    # ---------------------------------------------------------

    def test_string(self):

        assert "DecisionEngine" in str(self.engine)
        assert "DecisionEngine" in repr(self.engine)
