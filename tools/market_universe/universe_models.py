"""
=============================================================
Universe Data Models
=============================================================
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class Instrument:

    symbol: str

    token: str

    exchange: str

    segment: str

    expiry: str = ""

    strike: float = 0.0

    option_type: str = ""

    lot_size: int = 1

    tick_size: float = 0.05

    quantity: int = 1

    product: str = "INTRADAY"

    order_type: str = "MARKET"


@dataclass(slots=True)
class Universe:

    name: str

    instruments: List[Instrument] = field(default_factory=list)

    def add(self, instrument: Instrument) -> None:
        self.instruments.append(instrument)

    def __len__(self):
        return len(self.instruments)

    def __iter__(self):
        return iter(self.instruments)
