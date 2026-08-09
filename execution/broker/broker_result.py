"""
============================================================

Broker Result

============================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class BrokerResult:

    success: bool

    order_id: str

    message: str

    filled_quantity: int

    average_price: float | None
