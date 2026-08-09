"""
============================================================

Trading Symbol Model

============================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TradingSymbol:
    """
    Broker-independent instrument definition.
    """

    symbol: str
    exchange: str
    token: str

    instrument_type: str

    name: str

    expiry: str | None = None

    strike: float | None = None

    option_type: str | None = None
