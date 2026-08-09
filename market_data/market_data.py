"""
========================================================================

RUSI Trader AI

Market Data

Description
-----------
Represents one market snapshot for a trading instrument.

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from database.instrument import Instrument


@dataclass(frozen=True)
class MarketData:
    """
    Complete market snapshot for one instrument.
    """

    instrument: Instrument

    timestamp: datetime

    last_price: float

    open_price: float

    high_price: float

    low_price: float

    close_price: float

    volume: int

    open_interest: int = 0

    bid_price: float = 0.0

    ask_price: float = 0.0

    average_price: float = 0.0

    upper_circuit: float = 0.0

    lower_circuit: float = 0.0

    total_buy_quantity: int = 0

    total_sell_quantity: int = 0
