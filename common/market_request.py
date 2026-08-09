"""
============================================================

Market Request

Broker-independent market data request.

============================================================
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class MarketRequest:

    exchange: str

    symbol: str

    token: str

    interval: str

    from_datetime: datetime

    to_datetime: datetime
