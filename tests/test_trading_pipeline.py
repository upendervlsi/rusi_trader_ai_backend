"""
============================================================
RUSI Trader AI

V1.0

Trading Pipeline Tests
============================================================
"""

from tools.pipeline.pipeline_models import TradingRequest
from tools.pipeline.trading_pipeline import TradingPipeline


class MockScanner:

    def scan(self, request):
        return {"symbol": request.symbol}


class MockIndicator:

    def compute(self, scanner_result):
        return {"indicator": "ok"}


class MockDecision:

    def evaluate(self, indicator_result):
        return {"decision": "BUY"}


class MockConfidence:

    def calculate(self, decision_result):
        return {"confidence": 90.0}


class MockRisk:

    def evaluate(self, decision_result, confidence_result):
        return {"approved": True}


class MockPortfolio:

    def process(self, risk_result):
        return {"quantity": 10}


class MockExecution:

    def process(self, portfolio_result):
        return {"status": "FILLED"}


class TestTradingPipeline:

    def setup_method(self):

        self.pipeline = TradingPipeline(
            scanner_engine=MockScanner(),
            indicator_engine=MockIndicator(),
            decision_engine=MockDecision(),
            confidence_engine=MockConfidence(),
            risk_engine=MockRisk(),
            portfolio_engine=MockPortfolio(),
            execution_engine=MockExecution(),
        )

    # -------------------------------------------------

    def test_constructor(self):

        assert self.pipeline is not None

    # -------------------------------------------------

    def test_execute(self):

        request = TradingRequest(symbol="INFY")

        result = self.pipeline.execute(request)

        assert result.success
        assert result.context.request.symbol == "INFY"
        assert result.context.execution_result["status"] == "FILLED"

    # -------------------------------------------------

    def test_context(self):

        request = TradingRequest(symbol="TCS")

        result = self.pipeline.execute(request)

        assert result.context.scanner_result is not None
        assert result.context.indicator_result is not None
        assert result.context.decision_result is not None
        assert result.context.confidence_result is not None
        assert result.context.risk_result is not None
        assert result.context.portfolio_result is not None
        assert result.context.execution_result is not None

    # -------------------------------------------------

    def test_string(self):

        assert "TradingPipeline" in str(self.pipeline)
        assert "TradingPipeline" in repr(self.pipeline)
