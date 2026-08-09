"""
========================================================================

RUSI Trader AI

Paper Execution Engine

========================================================================
"""

from __future__ import annotations

import uuid

from intelligence.execution.execution_engine import (
    ExecutionEngine,
)
from intelligence.execution.execution_result import (
    ExecutionResult,
)
from intelligence.pipeline.trading_pipeline_result import (
    TradingPipelineResult,
)


class PaperExecutionEngine(
    ExecutionEngine
):

    def execute(
        self,
        result: TradingPipelineResult,
    ) -> ExecutionResult:

        if not result.risk_result.approved:

            return ExecutionResult(
                success=False,
                order_id="",
                status="REJECTED",
                message=result.risk_result.reason,
            )

        return ExecutionResult(
            success=True,
            order_id=str(uuid.uuid4()),
            status="PAPER_ORDER_CREATED",
            message="Paper trade executed successfully",
        )
