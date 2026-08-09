"""
========================================================================

RUSI Trader AI

Broker Response

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrokerResponse:

    success: bool

    order_id: str

    status: str

    message: str
