"""
============================================================
RUSI Trader AI

V1.0

Execution Order Models
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"


class OrderStatus(Enum):
    NEW = "NEW"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class TimeInForce(Enum):
    DAY = "DAY"
    IOC = "IOC"
    GTC = "GTC"


@dataclass(slots=True)
class OrderRequest:
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType = OrderType.MARKET
    price: float | None = None
    trigger_price: float | None = None
    time_in_force: TimeInForce = TimeInForce.DAY
    strategy: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrderResult:
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    filled_quantity: int = 0
    average_price: float = 0.0
    status: OrderStatus = OrderStatus.NEW
    broker_order_id: str = ""
    message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_open(self) -> bool:
        return self.status in (
            OrderStatus.NEW,
            OrderStatus.OPEN,
            OrderStatus.PARTIALLY_FILLED,
        )

    @property
    def is_completed(self) -> bool:
        return self.status in (
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
        )

    def __str__(self) -> str:
        return (
            f"OrderResult(order_id={self.order_id}, "
            f"symbol={self.symbol}, "
            f"status={self.status.value})"
        )

    __repr__ = __str__
