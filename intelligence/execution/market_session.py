"""
========================================================================

RUSI Trader AI

Market Session

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class MarketSession:

    exchange: str

    open_time: time

    close_time: time

    enabled: bool = True
