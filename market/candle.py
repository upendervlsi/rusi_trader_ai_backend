"""
============================================================
RUSI Trader AI

File : candle.py

Purpose :
    Standard OHLCV candle model.

Author : RUSI Trader AI
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Candle:
    """
    Standard market candle.
    """

    timestamp: datetime

    open: float

    high: float

    low: float

    close: float

    volume: float
