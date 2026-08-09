"""
============================================================
RUSI Trader AI

V1.0

Integration Manager
============================================================
"""

from __future__ import annotations

from tools.pipeline.pipeline_config import PipelineConfig
from tools.pipeline.trading_pipeline import TradingPipeline


class IntegrationManager:
    """
    Builds and validates the end-to-end trading pipeline.
    """

    def __init__(
        self,
        config: PipelineConfig,
        pipeline: TradingPipeline,
    ):

        self.config = config
        self.pipeline = pipeline

    # ---------------------------------------------------------

    def validate(self) -> bool:

        self.config.validate()

        if self.pipeline is None:
            raise ValueError("Trading pipeline is not configured.")

        return True

    # ---------------------------------------------------------

    def run(self, request):

        self.validate()

        return self.pipeline.execute(request)

    # ---------------------------------------------------------

    def __str__(self):

        return (
            "IntegrationManager("
            f"exchange={self.config.exchange}, "
            f"timeframe={self.config.timeframe})"
        )

    __repr__ = __str__
