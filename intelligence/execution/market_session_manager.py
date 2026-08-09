"""
========================================================================

RUSI Trader AI

Market Session Manager

========================================================================
"""

from __future__ import annotations

from datetime import datetime

from intelligence.execution.exchange import Exchange
from intelligence.execution.session_loader import (
    SessionLoader,
)


class MarketSessionManager:

    def __init__(self):

        self._sessions = SessionLoader().load()

    def is_open(
        self,
        exchange: Exchange,
    ) -> bool:

        now = datetime.now()

        if now.weekday() >= 5:
            return False

        session = self._sessions[exchange]

        if not session.enabled:
            return False

        return (
            session.open_time
            <= now.time()
            <= session.close_time
        )
