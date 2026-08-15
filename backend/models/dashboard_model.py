"""
============================================================

RUSI Trader AI

Dashboard Model

============================================================
"""

from pydantic import BaseModel

from backend.models.market_quote_model import (
    MarketQuoteModel,
)


class PortfolioSummaryModel(BaseModel):

    open_positions: int

    invested_amount: float

    market_value: float

    unrealized_pnl: float


class MarketPulseModel(BaseModel):

    """
    Compact market-level view used by the mobile dashboard.

    The dashboard displays the authoritative runtime values
    when available.

    Confidence is allowed to be None because a market that
    has not yet been evaluated must never receive a fabricated
    confidence value.
    """

    market: str

    display_name: str

    signal: str

    confidence: float | None

    status: str

    updated_time: str

    #
    # Market Pulse analysis information.
    #

    symbol: str = ""

    exchange: str = ""

    last_price: float | None = None

    trend: str = ""

    score: float | None = None

    reason: str = ""


class DashboardModel(BaseModel):

    market_status: str

    updated_time: str

    markets: list[MarketQuoteModel]

    market_pulse: list[MarketPulseModel]

    strongest_market: str | None

    strongest_confidence: float | None

    recommendation: str | None

    confidence: float | None

    portfolio: PortfolioSummaryModel
