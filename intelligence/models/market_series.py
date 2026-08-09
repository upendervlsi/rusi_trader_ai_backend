"""
========================================================================

RUSI Trader AI

Market Series

Description
-----------
Represents historical market data used by feature calculators.

All feature calculators receive a MarketSeries object instead of
individual price lists.

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from intelligence.core.enums import CandleInterval


@dataclass(slots=True)
class MarketSeries:
    """
    Historical market series.

    All lists must have identical length.
    """

    timestamps: List[datetime] = field(default_factory=list)

    open: List[float] = field(default_factory=list)

    high: List[float] = field(default_factory=list)

    low: List[float] = field(default_factory=list)

    close: List[float] = field(default_factory=list)

    volume: List[float] = field(default_factory=list)

    open_interest: List[float] = field(default_factory=list)

    interval: CandleInterval = CandleInterval.M1

    def __post_init__(self):

        size = len(self.close)

        fields = [
            self.timestamps,
            self.open,
            self.high,
            self.low,
            self.volume,
            self.open_interest,
        ]

        for value in fields:

            if len(value) not in (0, size):
                raise ValueError(
                    "All MarketSeries arrays must have identical length."
                )

    @property
    def length(self) -> int:
        return len(self.close)

    def is_empty(self) -> bool:
        return self.length == 0

    def latest_close(self) -> float:
        return self.close[-1]

    def latest_open(self) -> float:
        return self.open[-1]

    def latest_high(self) -> float:
        return self.high[-1]

    def latest_low(self) -> float:
        return self.low[-1]

    def latest_volume(self) -> float:
        return self.volume[-1]

    def latest_open_interest(self) -> float:
        return self.open_interest[-1]

    def validate(self) -> None:

        if self.is_empty():
            raise ValueError(
                "MarketSeries is empty."
            )

        for i in range(self.length):

            if self.high[i] < self.low[i]:
                raise ValueError(
                    f"Invalid candle at index {i}"
                )

            if self.volume and self.volume[i] < 0:
                raise ValueError(
                    f"Negative volume at index {i}"
                )
