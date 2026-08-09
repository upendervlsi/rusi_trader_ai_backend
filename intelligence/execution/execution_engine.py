"""
========================================================================

RUSI Trader AI

Execution Engine Base

========================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.execution.execution_result import ExecutionResult
from intelligence.pipeline.trading_pipeline_result import (
    TradingPipelineResult,
)


class ExecutionEngine(ABC):

    @abstractmethod
    def execute(
        self,
        result: TradingPipelineResult,
    ) -> ExecutionResult:
        """
        Execute a trading pipeline result.
        """
        raise NotImplementedError
