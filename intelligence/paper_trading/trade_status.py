"""
========================================================================

RUSI Trader AI

Trade Status

========================================================================
"""

from __future__ import annotations

from enum import Enum


class TradeStatus(str, Enum):

    OPEN = "OPEN"

    CLOSED = "CLOSED"

    STOP_LOSS = "STOP_LOSS"

    TARGET = "TARGET"
