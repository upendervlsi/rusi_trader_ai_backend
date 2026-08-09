"""
============================================================

Portfolio Summary

============================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioSummary:

    total_positions: int

    open_positions: int

    invested_amount: float

    market_value: float

    unrealized_pnl: float

    realized_pnl: float
