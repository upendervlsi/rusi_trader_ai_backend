"""
RUSI Trader AI

Market Model

API response model for the Market Module.

This model represents the latest market state
available from the Trading Runtime.
"""

from pydantic import BaseModel


class MarketModel(BaseModel):
    """
    Market API response model.

    The model separates:

    - market_status:
        Whether the exchange is currently OPEN/CLOSED.

    - data_status:
        Whether the market price data is LIVE,
        HISTORICAL, or another runtime-defined state.

    - live_price:
        Latest price obtained by the Market Data Engine.

    - latest_close:
        Latest completed candle close used by
        the technical-analysis pipeline.
    """

    # -----------------------------------------------------
    # Market Status
    # -----------------------------------------------------

    market_status: str

    data_status: str = "UNKNOWN"

    updated_time: str

    # -----------------------------------------------------
    # Live Price
    # -----------------------------------------------------

    live_price: float | None = None

    # -----------------------------------------------------
    # Historical / Analysis Price
    # -----------------------------------------------------

    latest_close: float | None = None

    # -----------------------------------------------------
    # Moving Averages
    # -----------------------------------------------------

    sma20: float | None = None

    sma50: float | None = None

    ema20: float | None = None

    ema50: float | None = None

    # -----------------------------------------------------
    # Market Structure
    # -----------------------------------------------------

    market_structure: str | None = None

    # -----------------------------------------------------
    # Future Runtime Fields
    #
    # These can be enabled when the runtime publishes them.
    # -----------------------------------------------------

    # open_price: float | None = None
    # high_price: float | None = None
    # low_price: float | None = None
    # previous_close: float | None = None
    # volume: float | None = None
    # vwap: float | None = None
    # rsi: float | None = None
    # macd: float | None = None
    # adx: float | None = None
    # atr: float | None = None
    # pcr: float | None = None
    # oi: int | None = None
    # change_oi: int | None = None
    # iv: float | None = None
    # max_pain: float | None = None
