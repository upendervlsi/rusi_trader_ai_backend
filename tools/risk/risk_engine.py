"""
============================================================
RUSI Trader AI

Risk Engine

Evaluates whether a trade should be executed based on
confidence and configurable risk limits.
============================================================
"""

from __future__ import annotations

from config.trading_config import TradingConfig
from tools.risk.risk_models import (
    RiskDecision,
    RiskResult,
)


class RiskEngine:
    """
    Basic risk evaluation engine.
    """

    def __init__(
        self,
        config: TradingConfig | None = None,
    ) -> None:

        self.config = config or TradingConfig()

    # ---------------------------------------------------------

    def evaluate(
        self,
        decision_result,
        capital: float,
        entry_price: float,
        stop_loss_price: float,
    ) -> RiskResult:

        result = RiskResult(
            decision=RiskDecision.ALLOW,
        )

        # -------------------------------
        # Confidence Check
        # -------------------------------

        if (
            decision_result.confidence
            < self.config.minimum_confidence
        ):

            result.decision = RiskDecision.REJECT

            result.add_reason(
                "Confidence below minimum threshold."
            )

            return result

        # -------------------------------
        # Risk Calculation
        # -------------------------------

        risk_amount = (
            capital
            * self.config.risk_per_trade
        )

        risk_per_share = max(
            entry_price - stop_loss_price,
            0.01,
        )

        position_size = (
            risk_amount / risk_per_share
        )

        result.position_size = position_size

        result.maximum_loss = risk_amount

        result.stop_loss = stop_loss_price

        result.risk_percent = (
            self.config.risk_per_trade * 100
        )

        result.add_reason(
            "Risk limits satisfied."
        )

        result.add_metadata(
            "capital",
            capital,
        )

        result.add_metadata(
            "risk_amount",
            risk_amount,
        )

        return result

    # ---------------------------------------------------------

    def __str__(self):

        return "RiskEngine()"

    def __repr__(self):

        return self.__str__()
