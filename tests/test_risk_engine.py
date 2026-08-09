"""
============================================================
RUSI Trader AI

Unit Tests

Risk Engine
============================================================
"""

from config.trading_config import TradingConfig
from tools.decision.decision_models import (
    DecisionResult,
    IndicatorSnapshot,
    SignalStrength,
    TradeSignal,
)
from tools.risk.risk_engine import RiskEngine
from tools.risk.risk_models import RiskDecision


class TestRiskEngine:

    def setup_method(self):

        self.engine = RiskEngine(
            TradingConfig()
        )

    # ---------------------------------------------------------

    def _decision(self, confidence):

        return DecisionResult(
            symbol="TEST",
            signal=TradeSignal.BUY,
            confidence=confidence,
            strength=SignalStrength.STRONG,
            indicators=IndicatorSnapshot(values={}),
        )

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.engine is not None

    # ---------------------------------------------------------

    def test_reject_low_confidence(self):

        result = self.engine.evaluate(
            decision_result=self._decision(40.0),
            capital=100000.0,
            entry_price=100.0,
            stop_loss_price=98.0,
        )

        assert result.decision == RiskDecision.REJECT

    # ---------------------------------------------------------

    def test_allow_trade(self):

        result = self.engine.evaluate(
            decision_result=self._decision(85.0),
            capital=100000.0,
            entry_price=100.0,
            stop_loss_price=98.0,
        )

        assert result.decision == RiskDecision.ALLOW

    # ---------------------------------------------------------

    def test_position_size(self):

        result = self.engine.evaluate(
            decision_result=self._decision(90.0),
            capital=100000.0,
            entry_price=100.0,
            stop_loss_price=98.0,
        )

        assert result.position_size > 0

    # ---------------------------------------------------------

    def test_metadata(self):

        result = self.engine.evaluate(
            decision_result=self._decision(90.0),
            capital=100000.0,
            entry_price=100.0,
            stop_loss_price=98.0,
        )

        assert "capital" in result.metadata
        assert "risk_amount" in result.metadata

    # ---------------------------------------------------------

    def test_string(self):

        assert "RiskEngine" in str(self.engine)
        assert "RiskEngine" in repr(self.engine)
