"""
========================================================================

RUSI Trader AI

Angel One Order Request

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AngelOrderRequest:

    variety: str

    tradingsymbol: str

    symboltoken: str

    transactiontype: str

    exchange: str

    ordertype: str

    producttype: str

    duration: str

    quantity: int

    price: float

    triggerprice: float = 0.0
