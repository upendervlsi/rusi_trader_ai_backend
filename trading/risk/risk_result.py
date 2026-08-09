"""
============================================================

RUSI Trader AI

Risk Result

============================================================
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RiskResult:
    """
    Final risk validation before execution.
    """

    approved: bool = False

    risk_score: float = 0.0

    position_size: int = 0

    stop_loss: float = 0.0

    target_price: float = 0.0

    risk_reward_ratio: float = 0.0

    reasons: list[str] = field(
        default_factory=list
    )

    def approve(self) -> None:

        self.approved = True

    def reject(
        self,
        reason: str,
    ) -> None:

        self.approved = False
        self.reasons.append(reason)
