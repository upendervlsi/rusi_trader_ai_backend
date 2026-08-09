"""
========================================================================

RUSI Trader AI

Backtest Engine

========================================================================
"""

from __future__ import annotations

from intelligence.backtest.backtest_result import BacktestResult
from intelligence.paper_trading.paper_portfolio import PaperPortfolio


class BacktestEngine:

    def evaluate(
        self,
        portfolio: PaperPortfolio,
    ) -> BacktestResult:

        total = len(portfolio.closed_trades)

        wins = sum(
            1
            for trade in portfolio.closed_trades
            if trade.pnl > 0
        )

        losses = total - wins

        if total == 0:
            win_rate = 0.0
        else:
            win_rate = wins / total * 100.0

        return BacktestResult(
            total_trades=total,
            winning_trades=wins,
            losing_trades=losses,
            win_rate=win_rate,
            net_pnl=portfolio.realized_pnl,
            reason="Backtest completed",
        )
