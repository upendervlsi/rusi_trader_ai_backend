"""
========================================================================

RUSI Trader AI

MACD Result

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class MACDResult:
    """
    Holds all MACD output series.
    """

    macd_line: List[float]

    signal_line: List[float]

    histogram: List[float]
