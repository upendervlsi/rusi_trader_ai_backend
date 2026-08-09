"""
========================================================================

RUSI Trader AI

Market Hours

========================================================================
"""

from __future__ import annotations

from datetime import datetime
from datetime import time


class MarketHours:

    MARKET_OPEN = time(9, 15)

    MARKET_CLOSE = time(15, 30)

    @classmethod
    def is_market_open(cls) -> bool:

        now = datetime.now()

        if now.weekday() >= 5:
            return False

        current = now.time()

        return cls.MARKET_OPEN <= current <= cls.MARKET_CLOSE
