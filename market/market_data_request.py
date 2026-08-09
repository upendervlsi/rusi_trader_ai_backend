"""
============================================================
RUSI Trader AI

File : market_data_request.py

Author : RUSI Trader AI
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from market.instrument import Instrument


@dataclass(slots=True)
class MarketDataRequest:
    """
    Standard historical data request.
    """

    instrument: Instrument

    interval: str

    from_datetime: datetime

    to_datetime: datetime
