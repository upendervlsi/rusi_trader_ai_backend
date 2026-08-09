"""
============================================================

Trading Position

============================================================
"""

from dataclasses import dataclass
from datetime import datetime

from execution.position_manager.position_status import (
    PositionStatus,
)


@dataclass(slots=True)
class Position:

    position_id: str

    order_id: str

    symbol: str

    exchange: str

    transaction_type: str

    quantity: int

    entry_price: float

    current_price: float

    unrealized_pnl: float

    realized_pnl: float

    entry_time: datetime

    status: PositionStatus
