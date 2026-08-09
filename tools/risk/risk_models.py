"""
============================================================
RUSI Trader AI

Risk Models

Shared data models for the Risk Management Engine.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class RiskDecision(Enum):
    """
    Final outcome of risk evaluation.
    """

    ALLOW = "ALLOW"
    REDUCE_POSITION = "REDUCE_POSITION"
    REJECT = "REJECT"


@dataclass
class RiskResult:
    """
    Output produced by the Risk Engine.
    """

    decision: RiskDecision

    position_size: float = 0.0

    stop_loss: float = 0.0

    target_price: float = 0.0

    risk_percent: float = 0.0

    reward_percent: float = 0.0

    risk_reward_ratio: float = 0.0

    maximum_loss: float = 0.0

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    reasons: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------

    def add_reason(self, reason: str) -> None:
        self.reasons.append(reason)

    # ---------------------------------------------------------

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata[key] = value

    # ---------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"RiskResult("
            f"decision={self.decision.value}, "
            f"position_size={self.position_size}, "
            f"risk_reward={self.risk_reward_ratio:.2f})"
        )

    __repr__ = __str__
