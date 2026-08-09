"""
========================================================================

RUSI Trader AI

Risk Manager

========================================================================
"""

from __future__ import annotations

from intelligence.risk.risk_result import RiskResult
from intelligence.trading.trade_plan import TradePlan


class RiskManager:

    DEFAULT_RISK_PERCENT = 1.0

    def evaluate(
        self,
        trade_plan: TradePlan,
        capital: float,
    ) -> RiskResult:

        max_risk_amount = (
            capital * self.DEFAULT_RISK_PERCENT / 100.0
        )

        risk_per_share = abs(
            trade_plan.entry_price -
            trade_plan.stop_loss
        )

        if risk_per_share <= 0.0:

            return RiskResult(
                approved=False,
                position_size=0,
                max_risk_amount=max_risk_amount,
                estimated_loss=0.0,
                reason="Invalid stop loss",
            )

        position_size = int(
            max_risk_amount / risk_per_share
        )

        estimated_loss = (
            position_size *
            risk_per_share
        )

        approved = position_size > 0

        return RiskResult(
            approved=approved,
            position_size=position_size,
            max_risk_amount=max_risk_amount,
            estimated_loss=estimated_loss,
            reason=(
                "Approved"
                if approved
                else "Position size is zero"
            ),
        )
