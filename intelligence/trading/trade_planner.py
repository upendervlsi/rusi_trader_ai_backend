"""
========================================================================

RUSI Trader AI

Trade Planner

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.decision.decision_result import DecisionResult
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.trading.trade_plan import TradePlan
from intelligence.signals.signal_type import SignalType


class TradePlanner:

    TARGET_MULTIPLIER = 2.0

    def create_plan(
        self,
        decision: DecisionResult,
        context: EvidenceContext,
    ) -> TradePlan:

        feature_store = context.feature_store

        price = feature_store.get_value(
            FeatureId.CLOSE_PRICE
        )

        atr = feature_store.get_value(
            FeatureId.ATR_14
        )

        if decision.signal == SignalType.BUY:

            entry = price
            stop = price - atr
            target = price + (atr * self.TARGET_MULTIPLIER)

        elif decision.signal == SignalType.SELL:

            entry = price
            stop = price + atr
            target = price - (atr * self.TARGET_MULTIPLIER)

        else:

            entry = price
            stop = price
            target = price

        return TradePlan(
            signal=decision.signal,
            entry_price=entry,
            stop_loss=stop,
            target_price=target,
            risk_reward=self.TARGET_MULTIPLIER,
            reason=decision.summary,
        )
