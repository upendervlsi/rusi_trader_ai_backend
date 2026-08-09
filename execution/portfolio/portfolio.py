"""
============================================================

Portfolio

============================================================
"""

from dataclasses import dataclass, field

from execution.position_manager.position import Position


@dataclass(slots=True)
class Portfolio:

    positions: list[Position] = field(default_factory=list)

    invested_amount: float = 0.0

    market_value: float = 0.0

    unrealized_pnl: float = 0.0

    realized_pnl: float = 0.0
