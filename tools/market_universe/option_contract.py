"""
=============================================================

RUSI Trader AI

Option Contract

Represents the broker option selected by the AI.

Sprint-18
=============================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OptionContract:

    #
    # Underlying
    #

    underlying_symbol: str

    #
    # Option
    #

    option_symbol: str

    exchange: str

    token: str

    strike: float

    expiry: str

    option_type: str

    lot_size: int

    #
    # Trade
    #

    recommendation: str
