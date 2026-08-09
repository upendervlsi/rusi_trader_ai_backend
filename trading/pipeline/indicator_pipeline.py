"""
========================================================================

RUSI Trader AI

Indicator Pipeline

========================================================================
"""

from __future__ import annotations

from indicators.indicator_manager import IndicatorManager
from trading.context.trading_context import TradingContext
from trading.pipeline.pipeline_stage import PipelineStage


class IndicatorPipeline(PipelineStage):

    def __init__(self):

        self._manager = IndicatorManager()

    @property
    def stage_name(self) -> str:

        return "Indicator Pipeline"

    def execute(
        self,
        context: TradingContext,
    ) -> TradingContext:

        #
        # Populate indicators inside snapshot
        #
        context.snapshot = self._manager.populate_snapshot(
            context.snapshot
        )

        #
        # Keep backward compatibility
        #
        context.indicators = context.snapshot.indicators

        return context
