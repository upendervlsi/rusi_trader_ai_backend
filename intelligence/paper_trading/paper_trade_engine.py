"""
========================================================================

RUSI Trader AI

Paper Trading Engine

========================================================================
"""

from __future__ import annotations

from intelligence.paper_trading.paper_trade import PaperTrade
from intelligence.risk.risk_result import RiskResult
from intelligence.trading.trade_plan import TradePlan


class PaperTradeEngine:

    def execute(
        self,
        trade_plan: TradePlan,
        risk_result: RiskResult,
    ) -> PaperTrade:

        if not risk_result.approved:

            return PaperTrade(
                signal=trade_plan.signal,
                entry_price=trade_plan.entry_price,
                quantity=0,
                stop_loss=trade_plan.stop_loss,
                target_price=trade_plan.target_price,
                status="REJECTED",
                pnl=0.0,
                reason=risk_result.reason,
            )

        return PaperTrade(
            signal=trade_plan.signal,
            entry_price=trade_plan.entry_price,
            quantity=risk_result.position_size,
            stop_loss=trade_plan.stop_loss,
            target_price=trade_plan.target_price,
            status="OPEN",
            pnl=0.0,
            reason="Paper trade opened",
        )
