"""
========================================================================

RUSI Trader AI

Execution Mode

========================================================================
"""

from __future__ import annotations

from enum import Enum


class ExecutionMode(str, Enum):

    BACKTEST = "BACKTEST"

    PAPER = "PAPER"

    LIVE = "LIVE"
