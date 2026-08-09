"""
========================================================================

RUSI Trader AI

Market Snapshot

Represents ONE immutable market snapshot.

No indicators.
No calculations.
No trading logic.

========================================================================
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from intelligence.core.enums import (
    CandleInterval,
    Exchange,
    InstrumentType,
    OptionType,
)


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    """
    Immutable market snapshot.
    """

    # Instrument
    exchange: Exchange
    symbol: str
    token: str
    instrument_type: InstrumentType

    # Time
    timestamp: datetime
    interval: CandleInterval

    # OHLC
    open: float
    high: float
    low: float
    close: float

    # Current Price
    ltp: float
    previous_close: float

    # Market Depth
    bid: float = 0.0
    ask: float = 0.0

    bid_quantity: int = 0
    ask_quantity: int = 0

    # Volume
    volume: int = 0

    average_volume: float = 0.0

    # Open Interest

    open_interest: int = 0

    previous_open_interest: int = 0

    # Derivatives

    expiry: Optional[str] = None

    strike: Optional[float] = None

    option_type: Optional[OptionType] = None

    def __post_init__(self):

        if self.high < self.low:
            raise ValueError(
                "High cannot be less than Low."
            )

        if self.open <= 0:
            raise ValueError(
                "Invalid Open Price."
            )

        if self.close <= 0:
            raise ValueError(
                "Invalid Close Price."
            )

        if self.ltp <= 0:
            raise ValueError(
                "Invalid LTP."
            )

        if self.volume < 0:
            raise ValueError(
                "Volume cannot be negative."
            )
