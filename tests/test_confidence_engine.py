"""
============================================================
RUSI Trader AI

Unit Tests

Confidence Engine
============================================================
"""

from tools.decision.confidence_engine import ConfidenceEngine


class TestConfidenceEngine:

    def setup_method(self):

        self.engine = ConfidenceEngine()

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.engine is not None

    # ---------------------------------------------------------

    def test_weights(self):

        assert self.engine.weights["ema_sma"] == 25.0
        assert self.engine.weights["rsi"] == 15.0
        assert self.engine.weights["macd"] == 20.0
        assert self.engine.weights["adx"] == 15.0
        assert self.engine.weights["supertrend"] == 15.0
        assert self.engine.weights["vwap"] == 10.0

    # ---------------------------------------------------------

    def test_calculate_empty(self):

        score, breakdown = self.engine.calculate({})

        assert score == 0.0
        assert isinstance(breakdown, dict)

        assert sum(breakdown.values()) == 0.0

    # ---------------------------------------------------------

    def test_calculate_positive(self):

        indicators = {
            "ema20": 110.0,
            "sma20": 100.0,
            "rsi14": 55.0,
            "macd": {
                "macd": 2.0,
                "signal": 1.0,
            },
            "adx14": 35.0,
            "supertrend": {
                "trend": "UP",
            },
            "vwap": 105.0,
        }

        score, breakdown = self.engine.calculate(
            indicators
        )

        assert score > 0.0

        assert breakdown["ema_sma"] == 25.0
        assert breakdown["rsi"] == 15.0
        assert breakdown["macd"] == 20.0
        assert breakdown["adx"] == 15.0
        assert breakdown["supertrend"] == 15.0
        assert breakdown["vwap"] == 10.0

        assert score == 100.0

    # ---------------------------------------------------------

    def test_string(self):

        assert "ConfidenceEngine" in str(self.engine)
        assert "ConfidenceEngine" in repr(self.engine)
