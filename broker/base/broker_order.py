"""
========================================================================

RUSI Trader AI

Broker Order

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.signals.signal_type import SignalType


@dataclass(frozen=True)
class BrokerOrder:

    symbol: str

    signal: SignalType

    quantity: int

    order_type: str

    product_type: str

    price: float

    stop_loss: float

    target_price: float
