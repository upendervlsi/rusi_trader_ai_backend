"""
============================================================
RUSI Trader AI

Portfolio Models

Shared portfolio data structures.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class Position:
    """
    Represents one open trading position.
    """

    symbol: str

    quantity: float

    entry_price: float

    current_price: float

    stop_loss: float

    target_price: float

    opened_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.entry_price

    @property
    def unrealized_pnl(self) -> float:
        return (
            self.current_price - self.entry_price
        ) * self.quantity


@dataclass
class PortfolioSummary:
    """
    Portfolio summary statistics.
    """

    available_cash: float

    invested_capital: float

    total_market_value: float

    unrealized_pnl: float

    realized_pnl: float

    open_positions: int

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )


@dataclass
class PortfolioState:
    """
    Complete portfolio state.
    """

    cash: float

    positions: dict[str, Position] = field(
        default_factory=dict
    )

    realized_pnl: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def add_position(
        self,
        position: Position,
    ) -> None:

        self.positions[position.symbol] = position

    def remove_position(
        self,
        symbol: str,
    ) -> None:

        self.positions.pop(symbol, None)

    def has_position(
        self,
        symbol: str,
    ) -> bool:

        return symbol in self.positions

    def __str__(self):

        return (
            f"PortfolioState("
            f"cash={self.cash}, "
            f"positions={len(self.positions)})"
        )

    __repr__ = __str__
