"""
============================================================

RUSI Trader AI

Trading Action

============================================================
"""

from enum import Enum


class TradingAction(str, Enum):
    """
    Supported trading actions.
    """

    BUY = "BUY"

    SELL = "SELL"

    HOLD = "HOLD"

    EXIT = "EXIT"

    WAIT = "WAIT"
