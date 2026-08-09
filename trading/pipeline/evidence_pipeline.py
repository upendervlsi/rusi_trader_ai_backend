"""
========================================================================

RUSI Trader AI

Evidence Pipeline

========================================================================
"""

from __future__ import annotations

from trading.context.trading_context import TradingContext


class EvidencePipeline:

    def __init__(self, evidence_engine):

        self._evidence_engine = evidence_engine

    def execute(
        self,
        context: TradingContext,
    ) -> TradingContext:

        context.evidence = (
            self._evidence_engine.evaluate(
                context
            )
        )

        return context
