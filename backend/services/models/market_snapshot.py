"""
============================================================

RUSI Trader AI

Market Snapshot

Single source of truth for all market related data.

============================================================
"""

from dataclasses import dataclass


@dataclass
class MarketSnapshot:

    # -------------------------------------------------------
    # Market
    # -------------------------------------------------------

    latest_close: float = 0.0

    market_status: str = "CLOSED"

    market_structure: str = "UNKNOWN"

    updated_time: str = ""

    # -------------------------------------------------------
    # Moving Averages
    # -------------------------------------------------------

    ema20: float = 0.0

    ema50: float = 0.0

    sma20: float = 0.0

    sma50: float = 0.0

    vwap: float = 0.0

    # -------------------------------------------------------
    # Momentum
    # -------------------------------------------------------

    rsi: float = 0.0

    macd: float = 0.0

    adx: float = 0.0

    atr: float = 0.0

    # -------------------------------------------------------
    # Option Analytics
    # -------------------------------------------------------

    pcr: float = 0.0

    open_interest: float = 0.0

    change_oi: float = 0.0

    implied_volatility: float = 0.0

    max_pain: float = 0.0

    # -------------------------------------------------------
    # AI
    # -------------------------------------------------------

    recommendation: str = "WAIT"

    confidence: float = 0.0

    engine_score: float = 0.0

    option_symbol: str = ""

    entry_price: float = 0.0

    stop_loss: float = 0.0

    target_price: float = 0.0
