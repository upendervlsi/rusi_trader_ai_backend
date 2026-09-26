"""
RUSI Trader AI

Stock Options Risk Engine

Stage 8A

Independent risk planning for stock-option BUY trades.

This module does not modify the existing NIFTY V1 risk path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from config.trading_config import TradingConfig


@dataclass(slots=True)
class StockOptionsRiskResult:
    allowed: bool
    entry_price: float = 0.0
    stop_loss: float = 0.0
    target_price: float = 0.0
    risk_per_unit: float = 0.0
    reward_per_unit: float = 0.0
    risk_reward_ratio: float = 0.0
    quantity: int = 0
    maximum_loss: float = 0.0
    maximum_reward: float = 0.0
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class StockOptionsRiskEngine:
    """
    Calculates the initial risk plan for a selected stock option.

    The selected option is always treated as a BUY transaction.
    """

    def __init__(
        self,
        config: TradingConfig | None = None,
    ) -> None:
        self.config = config or TradingConfig()

    def evaluate(
        self,
        entry_price: float,
        quantity: int,
    ) -> StockOptionsRiskResult:

        entry_price = float(entry_price)
        quantity = int(quantity)

        result = StockOptionsRiskResult(
            allowed=False,
            entry_price=entry_price,
            quantity=quantity,
        )

        if entry_price <= 0:
            result.reasons.append(
                "Invalid option entry price."
            )
            return result

        if quantity <= 0:
            result.reasons.append(
                "Invalid option quantity."
            )
            return result

        stop_loss = round(
            entry_price
            * (
                1.0
                - self.config.option_stop_loss_percent / 100.0
            ),
            2,
        )

        configured_target = (
            entry_price
            * (
                1.0
                + self.config.option_target_percent / 100.0
            )
        )

        risk_per_unit = entry_price - stop_loss

        if risk_per_unit <= 0:
            result.reasons.append(
                "Invalid calculated stop-loss."
            )
            return result

        minimum_reward = (
            risk_per_unit
            * self.config.minimum_risk_reward
        )

        minimum_target = entry_price + minimum_reward

        target_price = round(
            max(
                configured_target,
                minimum_target,
            ),
            2,
        )

        reward_per_unit = target_price - entry_price

        risk_reward_ratio = (
            reward_per_unit / risk_per_unit
            if risk_per_unit > 0
            else 0.0
        )

        maximum_loss = (
            risk_per_unit * quantity
        )

        maximum_reward = (
            reward_per_unit * quantity
        )

        if (
            risk_reward_ratio + 1e-9
            < self.config.minimum_risk_reward
        ):
            result.reasons.append(
                "Risk/reward below configured minimum."
            )
            return result

        result.allowed = True
        result.stop_loss = stop_loss
        result.target_price = target_price
        result.risk_per_unit = risk_per_unit
        result.reward_per_unit = reward_per_unit
        result.risk_reward_ratio = risk_reward_ratio
        result.maximum_loss = maximum_loss
        result.maximum_reward = maximum_reward

        result.reasons.append(
            "Stock-option risk limits satisfied."
        )

        result.metadata.update(
            {
                "option_stop_loss_percent": (
                    self.config.option_stop_loss_percent
                ),
                "option_target_percent": (
                    self.config.option_target_percent
                ),
                "minimum_risk_reward": (
                    self.config.minimum_risk_reward
                ),
            }
        )

        return result
