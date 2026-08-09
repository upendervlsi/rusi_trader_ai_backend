"""
========================================================================

RUSI Trader AI

Instrument

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.execution.exchange import Exchange


@dataclass(frozen=True)
class Instrument:
    """
    Trading instrument.
    """

    symbol: str

    exchange: Exchange

    symbol_token: str = ""

    lot_size: int = 1

    tick_size: float = 0.05
