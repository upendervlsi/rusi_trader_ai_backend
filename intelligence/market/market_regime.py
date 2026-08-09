"""
========================================================================

RUSI Trader AI

Market Regime

========================================================================
"""

from __future__ import annotations

from enum import Enum


class MarketRegime(str, Enum):

    TRENDING = "TRENDING"

    RANGING = "RANGING"

    HIGH_VOLATILITY = "HIGH_VOLATILITY"

    LOW_VOLATILITY = "LOW_VOLATILITY"

    UNKNOWN = "UNKNOWN"
