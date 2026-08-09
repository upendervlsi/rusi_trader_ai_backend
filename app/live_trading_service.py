"""
========================================================================

RUSI Trader AI

Live Trading Service

Description
-----------
Coordinates the trading pipeline and execution engine.

========================================================================
"""

from __future__ import annotations

from intelligence.execution.execution_engine import ExecutionEngine
from intelligence.pipeline.trading_pipeline import TradingPipeline
from intelligence.pipeline.trading_pipeline_result import (
    TradingPipelineResult,
)


class LiveTradingService:

    def __init__(
        self,
        pipeline: TradingPipeline,
        execution_engine: ExecutionEngine,
    ) -> None:

        self._pipeline = pipeline
        self._execution_engine = execution_engine

    def process(
        self,
        pipeline_result: TradingPipelineResult,
    ):

        if not pipeline_result.risk_result.approved:
            return None

        return self._execution_engine.execute(
            pipeline_result,
        )
