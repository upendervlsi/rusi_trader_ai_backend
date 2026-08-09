"""
========================================================================

RUSI Trader AI

Decision Pipeline

========================================================================
"""

from __future__ import annotations

from trading.context.trading_context import TradingContext


class DecisionPipeline:

    def __init__(self, decision_engine):

        self._decision_engine = decision_engine

    def execute(
        self,
        context: TradingContext,
    ) -> TradingContext:

        context.decision = (
            self._decision_engine.evaluate(
                context
            )
        )

        return context
