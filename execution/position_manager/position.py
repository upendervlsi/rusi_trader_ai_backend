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

    token: str

    transaction_type: str

    quantity: int

    entry_price: float

    current_price: float

    #
    # Profit protection state
    #

    highest_price: float

    highest_unrealized_pnl: float

    profit_protection_active: bool

    protected_price: float

    #
    # Market reversal confirmation state
    #

    reversal_count: int

    last_reversal_signal: str

    # Option trade risk levels

    stop_loss: float

    target_price: float

    unrealized_pnl: float

    realized_pnl: float

    entry_time: datetime

    # Exit information.
    # Populated only after the position is closed.
    exit_time: datetime | None

    exit_reason: str

    status: PositionStatus
