"""
============================================================
RUSI Trader AI

Indicator Bundle

Central container for calculated technical indicators.

============================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class IndicatorBundle:

    # -------------------------------------------------------
    # Moving Averages
    # -------------------------------------------------------

    sma20: float | None = None
    sma50: float | None = None
    sma200: float | None = None

    ema20: float | None = None
    ema50: float | None = None
    ema200: float | None = None

    # -------------------------------------------------------
    # Volume / Price
    # -------------------------------------------------------

    vwap: float | None = None

    # -------------------------------------------------------
    # Momentum
    # -------------------------------------------------------

    rsi14: float | None = None

    adx14: float | None = None

    atr14: float | None = None

    # -------------------------------------------------------
    # MACD
    # -------------------------------------------------------

    macd: float | None = None

    signal_line: float | None = None

    histogram: float | None = None
