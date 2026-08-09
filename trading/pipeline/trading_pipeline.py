"""
========================================================================

RUSI Trader AI

Trading Pipeline

========================================================================
"""

from __future__ import annotations

from trading.context.trading_context import TradingContext
from trading.pipeline.pipeline_stage import PipelineStage
from time import perf_counter

from trading.pipeline.pipeline_result import PipelineResult

class TradingPipeline:

    def __init__(
        self,
        stages: list[PipelineStage],
    ):
        self._stages = stages

    def execute(
        self,
        context,
    ):

        for stage in self._stages:

            start = perf_counter()

            stage.before_execute(context)

            context = stage.execute(context)

            stage.after_execute(context)

            elapsed = (
                perf_counter() - start
            ) * 1000.0

            context.pipeline_results.append(
                PipelineResult(
                    stage_name=stage.stage_name,
                    success=True,
                    execution_time_ms=elapsed,
                )
            )

        return context
