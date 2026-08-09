"""
========================================================================

RUSI Trader AI

Signal Types

========================================================================
"""

from enum import Enum


class SignalType(Enum):
    """
    Standard trading signals.
    """

    STRONG_BUY = "STRONG_BUY"

    BUY = "BUY"

    HOLD = "HOLD"

    SELL = "SELL"

    STRONG_SELL = "STRONG_SELL"
