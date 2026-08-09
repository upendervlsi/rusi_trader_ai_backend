"""
========================================================================

RUSI Trader AI

Session Loader

========================================================================
"""

from __future__ import annotations

from datetime import datetime

import yaml

from intelligence.execution.exchange import Exchange
from intelligence.execution.market_session import (
    MarketSession,
)


class SessionLoader:

    def __init__(
        self,
        filename: str = "config/market_sessions.yaml",
    ):

        self._filename = filename

    def load(self):

        with open(
            self._filename,
            "r",
            encoding="utf-8",
        ) as fp:

            cfg = yaml.safe_load(fp)

        sessions = {}

        for name, item in cfg["markets"].items():

            first = item["sessions"][0]

            sessions[
                Exchange(name)
            ] = MarketSession(
                exchange=name,
                open_time=datetime.strptime(
                    first["open"],
                    "%H:%M",
                ).time(),
                close_time=datetime.strptime(
                    first["close"],
                    "%H:%M",
                ).time(),
                enabled=item["enabled"],
            )

        return sessions
