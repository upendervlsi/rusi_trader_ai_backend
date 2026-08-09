"""
========================================================================

RUSI Trader AI

Backtest Result

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestResult:

    total_trades: int

    winning_trades: int

    losing_trades: int

    win_rate: float

    net_pnl: float

    reason: str
