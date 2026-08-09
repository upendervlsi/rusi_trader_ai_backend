"""
============================================================

RUSI Trader AI

Indicators API

Exposes the technical indicators produced by the
authoritative Trading Runtime.

Data flow:

    Angel One
        |
        v
    MarketDataEngine
        |
        v
    ExecutionManager
        |
        v
    RuntimeManager
        |
        v
    TradingEngineFacade
        |
        v
    MarketService / Indicators API
        |
        v
      Flutter

This API does NOT calculate indicators itself.

It only exposes the indicators already calculated
and published by the Trading Runtime.

============================================================
"""

from fastapi import APIRouter

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)


router = APIRouter(
    prefix="/api",
    tags=["Indicators"],
)


# ============================================================
# Trading Runtime
# ============================================================

facade = TradingEngineFacade()


# ============================================================
# Indicators
# ============================================================

@router.get("/indicators")
def get_indicators():
    """
    Return the latest indicators from the authoritative
    Trading Runtime snapshot.

    No broker communication happens here.

    No indicator calculation happens here.
    """

    # --------------------------------------------------------
    # Runtime
    # --------------------------------------------------------

    state = facade.get_runtime_state()

    snapshot = state.snapshot

    # --------------------------------------------------------
    # Runtime not ready
    # --------------------------------------------------------

    if snapshot is None:

        return {
            "ema20": 0.0,
            "ema50": 0.0,
            "sma20": 0.0,
            "sma50": 0.0,
            "vwap": 0.0,
            "data_status": getattr(
                state,
                "data_status",
                "UNKNOWN",
            ) or "UNKNOWN",
            "updated_time": getattr(
                state,
                "updated_time",
                "",
            ),
        }

    # --------------------------------------------------------
    # Indicator bundle
    # --------------------------------------------------------

    indicators = getattr(
        snapshot,
        "indicators",
        None,
    )

    # --------------------------------------------------------
    # No indicator bundle
    # --------------------------------------------------------

    if indicators is None:

        return {
            "ema20": 0.0,
            "ema50": 0.0,
            "sma20": 0.0,
            "sma50": 0.0,
            "vwap": 0.0,
            "data_status": getattr(
                state,
                "data_status",
                "UNKNOWN",
            ) or "UNKNOWN",
            "updated_time": getattr(
                state,
                "updated_time",
                "",
            ),
        }

    # --------------------------------------------------------
    # Real runtime indicators
    # --------------------------------------------------------

    return {

        "ema20": getattr(
            indicators,
            "ema20",
            0.0,
        ),

        "ema50": getattr(
            indicators,
            "ema50",
            0.0,
        ),

        "sma20": getattr(
            indicators,
            "sma20",
            0.0,
        ),

        "sma50": getattr(
            indicators,
            "sma50",
            0.0,
        ),

        "vwap": getattr(
            indicators,
            "vwap",
            0.0,
        ),

        "data_status": getattr(
            state,
            "data_status",
            "UNKNOWN",
        ) or "UNKNOWN",

        "updated_time": getattr(
            state,
            "updated_time",
            "",
        ),
    }
