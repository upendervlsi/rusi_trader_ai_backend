"""
============================================================
RUSI Trader AI

V1.0

Integration Manager Tests
============================================================
"""

import pytest

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
            message=f"Executed {request.symbol}",
        )


class TestIntegrationManager:

    def setup_method(self):

        self.config = PipelineConfig()

        self.pipeline = MockPipeline()

        self.manager = IntegrationManager(
            config=self.config,
            pipeline=self.pipeline,
        )

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.manager is not None

    # ---------------------------------------------------------

    def test_validate(self):

        assert self.manager.validate() is True

    # ---------------------------------------------------------

    def test_run(self):

        request = TradingRequest(symbol="INFY")

        result = self.manager.run(request)

        assert result.success
        assert result.message == "Executed INFY"

    # ---------------------------------------------------------

    def test_pipeline_none(self):

        manager = IntegrationManager(
            config=self.config,
            pipeline=None,
        )

        with pytest.raises(ValueError):

            manager.validate()

    # ---------------------------------------------------------

    def test_string(self):

        assert "IntegrationManager" in str(self.manager)
        assert "IntegrationManager" in repr(self.manager)
