"""
============================================================
RUSI Trader AI

Market Data Models

Technology-independent market data structures.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ============================================================
# OHLCV Candle
# ============================================================

@dataclass(slots=True)
class Candle:
    """
    Represents one OHLCV candle.
    """

    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float

    open_interest: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Market Data
# ============================================================

@dataclass(slots=True)
class MarketData:
    """
    Market data returned by a MarketDataProvider.
    """

    symbol: str

    exchange: str

    timeframe: str

    candles: list[Candle] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def latest(self) -> Candle | None:
        """
        Return the latest candle.
        """

        if not self.candles:
            return None

        return self.candles[-1]

    def __len__(self) -> int:
        return len(self.candles)
