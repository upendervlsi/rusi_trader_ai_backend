"""
========================================================================

RUSI Trader AI

Paper Portfolio

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence.paper_trading.paper_trade import PaperTrade


@dataclass
class PaperPortfolio:

    capital: float

    available_capital: float

    realized_pnl: float = 0.0

    open_trades: list[PaperTrade] = field(default_factory=list)

    closed_trades: list[PaperTrade] = field(default_factory=list)
