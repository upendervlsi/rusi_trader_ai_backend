"""
========================================================================

RUSI Trader AI

Risk Result

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:

    approved: bool

    position_size: int

    max_risk_amount: float

    estimated_loss: float

    reason: str
