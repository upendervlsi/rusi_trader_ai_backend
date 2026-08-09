"""
========================================================================

RUSI Trader AI

Evidence Context Builder

Description
-----------
Builds an EvidenceContext from the TradingContext.

This isolates the Evidence subsystem from the Trading pipeline and
keeps ExecutionManager clean.

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.evidence_context import EvidenceContext
from trading.context.trading_context import TradingContext


class EvidenceContextBuilder:
    """
    Builds EvidenceContext instances.
    """

    @staticmethod
    def build(
        trading_context: TradingContext,
    ) -> EvidenceContext:

        return EvidenceContext(
            feature_store=trading_context.features,
            macd_result=None,
        )
