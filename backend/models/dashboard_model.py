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


class DashboardModel(BaseModel):

    market_status: str

    updated_time: str

    markets: list[MarketQuoteModel]

    recommendation: str | None

    confidence: float | None

    portfolio: PortfolioSummaryModel
