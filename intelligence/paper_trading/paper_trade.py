"""
========================================================================

RUSI Trader AI

Paper Trade

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.signals.signal_type import SignalType


@dataclass(frozen=True)
class PaperTrade:

    signal: SignalType

    entry_price: float

    quantity: int

    stop_loss: float

    target_price: float

    status: str

    pnl: float

    reason: str
