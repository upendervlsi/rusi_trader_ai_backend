"""
========================================================================

RUSI Trader AI

Paper Trade

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from intelligence.signals.signal_type import SignalType


@dataclass(frozen=True)
class PaperTrade:

    # ================================================================
    # SIGNAL
    # ================================================================

    signal: SignalType

    # ================================================================
    # SELECTED OPTION CONTRACT
    # ================================================================

    option_symbol: str = ""

    option_token: str = ""

    exchange: str = ""

    strike: float = 0.0

    expiry: str = ""

    option_type: str = ""

    # ================================================================
    # OPTION PREMIUM TRADE
    # ================================================================

    entry_price: float = 0.0

    quantity: int = 0

    stop_loss: float = 0.0

    target_price: float = 0.0

    # ================================================================
    # RUNTIME
    # ================================================================

    status: str = "OPEN"

    pnl: float = 0.0

    current_price: float = 0.0

    reason: str = ""

    # ================================================================
    # TRADE TIMING
    # ================================================================

    entry_time: datetime | None = None

    exit_time: datetime | None = None
