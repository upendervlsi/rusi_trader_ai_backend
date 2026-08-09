"""
============================================================
RUSI Trader AI

V1.0

End-to-End Pipeline Tests
============================================================
"""

from tools.pipeline.integration_manager import IntegrationManager
from tools.pipeline.pipeline_config import PipelineConfig
from tools.pipeline.pipeline_models import (
    PipelineResult,
    TradingRequest,
)


class MockPipeline:

    def execute(self, request):

        return PipelineResult(
            success=True,
            context=None,
            message=f"Pipeline completed for {request.symbol}",
        )


class TestEndToEndPipeline:

    def setup_method(self):

        self.manager = IntegrationManager(
            config=PipelineConfig(),
            pipeline=MockPipeline(),
        )

    # ---------------------------------------------------------

    def test_pipeline_execution(self):

        request = TradingRequest(symbol="INFY")

        result = self.manager.run(request)

        assert result.success
        assert result.message == "Pipeline completed for INFY"

    # ---------------------------------------------------------

    def test_multiple_symbols(self):

        symbols = [
            "INFY",
            "TCS",
            "RELIANCE",
            "SBIN",
            "HDFCBANK",
        ]

        for symbol in symbols:

            result = self.manager.run(
                TradingRequest(symbol=symbol)
            )

            assert result.success

    # ---------------------------------------------------------

    def test_validation_before_execution(self):

        assert self.manager.validate()

    # ---------------------------------------------------------

    def test_pipeline_result_type(self):

        result = self.manager.run(
            TradingRequest(symbol="NIFTY")
        )

        assert isinstance(result, PipelineResult)

    # ---------------------------------------------------------

    def test_string(self):

        assert "IntegrationManager" in str(self.manager)
