"""
========================================================================

RUSI Trader AI

Risk Pipeline

========================================================================
"""

from __future__ import annotations

from trading.context.trading_context import TradingContext


class RiskPipeline:

    def __init__(self, risk_manager):

        self._risk_manager = risk_manager

    def execute(
        self,
        context: TradingContext,
    ) -> TradingContext:

        context.risk_result = (
            self._risk_manager.evaluate(
                context
            )
        )

        return context
