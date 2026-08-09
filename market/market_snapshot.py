"""
============================================================
RUSI Trader AI

File : market_snapshot.py

Purpose :
    Standard market snapshot shared by all AI engines.

Author : RUSI Trader AI
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from market.instrument import Instrument
from market.candle import Candle


@dataclass(slots=True)
class MarketSnapshot:
    """
    Complete market state.
    """

    instrument: Instrument

    candles: list[Candle] = field(default_factory=list)
