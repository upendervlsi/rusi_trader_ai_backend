"""
============================================================

RUSI Trader AI

Market Quote Model

Represents one market instrument.

============================================================
"""

from pydantic import BaseModel


class MarketQuoteModel(BaseModel):

    symbol: str

    exchange: str

    last_price: float | None = None

    signal: str | None = None

    trend: str | None = None

    updated_time: str
