"""
========================================================================

RUSI Trader AI

Exchange

========================================================================
"""

from __future__ import annotations

from enum import Enum


class Exchange(str, Enum):

    NSE = "NSE"

    BSE = "BSE"

    MCX = "MCX"

    NSE_FO = "NSE_FO"

    CDS = "CDS"
