"""
============================================================

RUSI Trader AI

Market Snapshot

Single object representing the complete
market state for AI evaluation.

============================================================
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class MarketSnapshot:

    market: Any

    indicators: Any

    momentum: Any

    options: Any

    timestamp: str | None = None
