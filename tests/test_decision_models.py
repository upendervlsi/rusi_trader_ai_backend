"""
============================================================
RUSI Trader AI

Unit Tests

Decision Models
============================================================
"""

from tools.decision.decision_models import (
    DecisionResult,
    IndicatorSnapshot,
    SignalStrength,
    TradeSignal,
)


class TestDecisionModels:

    def test_trade_signal_enum(self):

        assert TradeSignal.BUY.value == "BUY"
        assert TradeSignal.SELL.value == "SELL"
        assert TradeSignal.HOLD.value == "HOLD"

    # ---------------------------------------------------------

    def test_signal_strength_enum(self):

        assert SignalStrength.VERY_WEAK.value == "VERY_WEAK"
        assert SignalStrength.WEAK.value == "WEAK"
        assert SignalStrength.MEDIUM.value == "MEDIUM"
        assert SignalStrength.STRONG.value == "STRONG"
        assert SignalStrength.VERY_STRONG.value == "VERY_STRONG"

    # ---------------------------------------------------------

    def test_indicator_snapshot(self):

        snapshot = IndicatorSnapshot(
            values={
                "ema20": 100.5,
                "rsi14": 62.4,
            }
        )

        assert snapshot.values["ema20"] == 100.5
        assert snapshot.values["rsi14"] == 62.4

    # ---------------------------------------------------------

    def test_decision_result(self):

        result = DecisionResult(
            symbol="RELIANCE",
            signal=TradeSignal.BUY,
            confidence=92.5,
            strength=SignalStrength.STRONG,
            indicators=IndicatorSnapshot(),
        )

        assert result.symbol == "RELIANCE"
        assert result.signal == TradeSignal.BUY
        assert result.confidence == 92.5
        assert result.strength == SignalStrength.STRONG

    # ---------------------------------------------------------

    def test_add_reason(self):

        result = DecisionResult(
            symbol="SBIN",
            signal=TradeSignal.BUY,
            confidence=80,
            strength=SignalStrength.MEDIUM,
            indicators=IndicatorSnapshot(),
        )

        result.add_reason("EMA crossed SMA")

        assert len(result.reasons) == 1
        assert result.reasons[0] == "EMA crossed SMA"

    # ---------------------------------------------------------

    def test_add_metadata(self):

        result = DecisionResult(
            symbol="INFY",
            signal=TradeSignal.HOLD,
            confidence=60,
            strength=SignalStrength.WEAK,
            indicators=IndicatorSnapshot(),
        )

        result.add_metadata(
            "strategy",
            "Momentum"
        )

        assert result.metadata["strategy"] == "Momentum"

    # ---------------------------------------------------------

    def test_timestamp_created(self):

        result = DecisionResult(
            symbol="TCS",
            signal=TradeSignal.SELL,
            confidence=45,
            strength=SignalStrength.WEAK,
            indicators=IndicatorSnapshot(),
        )

        assert result.timestamp is not None
