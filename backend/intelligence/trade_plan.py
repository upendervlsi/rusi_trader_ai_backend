"""
============================================================

RUSI Trader AI

Trade Plan

============================================================
"""

from dataclasses import dataclass


@dataclass
class TradePlan:

    recommendation: str

    confidence: float

    trade_quality: float

    entry_price: float | None

    stop_loss: float | None

    target1: float | None

    target2: float | None

    risk_reward: str

    position_size: str

    holding_type: str

    risk: str

    reasons: list[str]
