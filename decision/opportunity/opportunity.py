"""
============================================================

Trading Opportunity

============================================================
"""

from dataclasses import dataclass


@dataclass
class TradingOpportunity:

    symbol: str = ""

    exchange: str = ""

    signal: str = ""

    confidence: float = 0.0

    score: float = 0.0

    opportunity_score: float = 0.0

    recommendation = None
