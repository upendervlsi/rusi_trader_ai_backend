"""
========================================================================

RUSI Trader AI

Trade Plan

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.signals.signal_type import SignalType


@dataclass(frozen=True)
class TradePlan:

    signal: SignalType

    entry_price: float

    stop_loss: float

    target_price: float

    risk_reward: float

    reason: str
