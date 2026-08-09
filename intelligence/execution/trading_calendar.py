"""
========================================================================

RUSI Trader AI

Trading Calendar

========================================================================
"""

from __future__ import annotations

from database.instrument import Instrument
from intelligence.execution.market_session_manager import (
    MarketSessionManager,
)


class TradingCalendar:

    def __init__(self):

        self._session_manager = MarketSessionManager()

    def is_tradable(
        self,
        instrument: Instrument,
    ) -> bool:

        return self._session_manager.is_open(
            instrument.exchange,
        )
