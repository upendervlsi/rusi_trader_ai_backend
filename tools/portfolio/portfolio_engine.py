"""
============================================================
RUSI Trader AI

V1.0

Portfolio Engine
============================================================
"""

from __future__ import annotations

from tools.portfolio.portfolio_models import (
    PortfolioState,
    PortfolioSummary,
    Position,
)


class PortfolioEngine:
    """
    Manages portfolio positions and cash.
    """

    def __init__(
        self,
        initial_cash: float,
    ) -> None:

        self.state = PortfolioState(
            cash=initial_cash,
        )

    # ---------------------------------------------------------

    def open_position(
        self,
        position: Position,
    ) -> None:

        cost = position.cost_basis

        if cost > self.state.cash:
            raise ValueError(
                "Insufficient cash to open position."
            )

        self.state.cash -= cost

        self.state.add_position(position)

    # ---------------------------------------------------------

    def close_position(
        self,
        symbol: str,
    ) -> Position:

        if symbol not in self.state.positions:
            raise KeyError(symbol)

        position = self.state.positions[symbol]

        proceeds = position.market_value

        self.state.cash += proceeds

        self.state.realized_pnl += (
            position.unrealized_pnl
        )

        self.state.remove_position(symbol)

        return position

    # ---------------------------------------------------------

    def get_position(
        self,
        symbol: str,
    ) -> Position | None:

        return self.state.positions.get(symbol)

    # ---------------------------------------------------------

    def portfolio_summary(
        self,
    ) -> PortfolioSummary:

        invested = sum(
            p.cost_basis
            for p in self.state.positions.values()
        )

        market_value = sum(
            p.market_value
            for p in self.state.positions.values()
        )

        unrealized = sum(
            p.unrealized_pnl
            for p in self.state.positions.values()
        )

        return PortfolioSummary(
            available_cash=self.state.cash,
            invested_capital=invested,
            total_market_value=market_value,
            unrealized_pnl=unrealized,
            realized_pnl=self.state.realized_pnl,
            open_positions=len(
                self.state.positions
            ),
        )

    # ---------------------------------------------------------

    def __str__(self):

        return (
            "PortfolioEngine("
            f"cash={self.state.cash}, "
            f"positions={len(self.state.positions)})"
        )

    __repr__ = __str__
