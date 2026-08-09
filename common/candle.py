"""
============================================================

Candle Model

Internal broker-independent OHLCV candle.

============================================================
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Candle:

    timestamp: datetime

    open: float

    high: float

    low: float

    close: float

    volume: int
