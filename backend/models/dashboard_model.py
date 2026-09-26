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


class TodayPnLModel(BaseModel):

    realized_pnl: float

    unrealized_pnl: float

    net_pnl: float


class CurrentTradeModel(BaseModel):

    position_id: str

    symbol: str

    exchange: str

    transaction_type: str

    quantity: int

    entry_price: float

    current_price: float

    current_pnl: float

    stop_loss: float

    target_price: float

    protection: str

    status: str

    entry_time: str


class AITradeSignalModel(BaseModel):

    direction: str | None

    confidence: float | None

    score: float | None

    option: str | None

    option_symbol: str | None

    signal_status: str


class TodayExecutionModel(BaseModel):

    trades: int

    wins: int

    losses: int

    win_rate: float


class TradeHistoryModel(BaseModel):

    position_id: str

    symbol: str

    exchange: str

    option_type: str

    transaction_type: str

    quantity: int

    entry_price: float

    exit_price: float | None

    pnl: float

    exit_reason: str

    entry_time: str

    exit_time: str | None


class CurrentMarketSignalModel(BaseModel):

    symbol: str

    display_name: str

    signal: str | None

    confidence: float | None

    score: float | None

    last_price: float | None

    updated_time: str


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

    today_pnl: TodayPnLModel

    current_trade: CurrentTradeModel | None

    ai_trade_signal: AITradeSignalModel

    today_execution: TodayExecutionModel

    trade_history: list[TradeHistoryModel]

    current_market_signal: CurrentMarketSignalModel
