"""
============================================================
RUSI Trader AI

V1.0

Pipeline Configuration Tests
============================================================
"""

import pytest

from tools.pipeline.pipeline_config import PipelineConfig


class TestPipelineConfig:

    def test_default_values(self):

        config = PipelineConfig()

        assert config.paper_trading is True
        assert config.exchange == "NSE"
        assert config.timeframe == "5m"

        assert config.scanner_enabled
        assert config.indicator_enabled
        assert config.decision_enabled
        assert config.confidence_enabled
        assert config.risk_enabled
        assert config.portfolio_enabled
        assert config.execution_enabled

    # -----------------------------------------------------

    def test_validation_success(self):

        config = PipelineConfig()

        config.validate()

    # -----------------------------------------------------

    def test_empty_exchange(self):

        config = PipelineConfig(exchange="")

        with pytest.raises(ValueError):
            config.validate()

    # -----------------------------------------------------

    def test_empty_timeframe(self):

        config = PipelineConfig(timeframe="")

        with pytest.raises(ValueError):
            config.validate()

    # -----------------------------------------------------

    def test_live_mode(self):

        config = PipelineConfig(paper_trading=False)

        assert config.paper_trading is False

    # -----------------------------------------------------

    def test_string(self):

        config = PipelineConfig()

        assert "PipelineConfig" in str(config)
        assert "PipelineConfig" in repr(config)
