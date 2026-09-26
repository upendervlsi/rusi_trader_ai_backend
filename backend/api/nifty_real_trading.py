"""
============================================================
RUSI Trader AI

NIFTY Real Trading API

Controls NEW NIFTY real-trading entries
and exposes persistent NIFTY real-trade history.

IMPORTANT:
    - Does not stop the TradingEngineService.
    - Does not affect existing-position monitoring/exits.
    - Does not affect Paper Trading.
    - Does not affect MIDCAP or other markets.
    - Trade-history endpoints are READ ONLY.
    - Trade-history endpoints do not place broker orders.
============================================================
"""

from fastapi import APIRouter, HTTPException

from backend.services.trading_engine_service import (
    TradingEngineService,
)

from core.nifty_real_pnl_store import (
    NiftyRealPnlStore,
)


router = APIRouter(
    prefix="/api/nifty-real-trading",
    tags=["NIFTY Real Trading"],
)


def _get_nifty_manager():

    service = TradingEngineService()

    manager = service.get_nifty_manager()

    if manager is None:

        raise HTTPException(
            status_code=503,
            detail="NIFTY ExecutionManager is not initialized.",
        )

    return manager


def _get_real_pnl_store() -> NiftyRealPnlStore:

    return NiftyRealPnlStore()


def _round_pnl_value(value):
    """Normalize financial P&L values to two decimal places."""

    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def _normalize_trade_pnl(trade):

    if not isinstance(trade, dict):
        return trade

    normalized = dict(trade)

    if "realized_pnl" in normalized:
        normalized["realized_pnl"] = _round_pnl_value(
            normalized["realized_pnl"]
        )

    return normalized


@router.get("/status")
def get_status():

    manager = _get_nifty_manager()

    return {
        "status": "SUCCESS",
        "real_trading": (
            manager.get_nifty_real_trading_status()
        ),
    }


@router.post("/enable")
def enable_real_trading():

    manager = _get_nifty_manager()

    enabled = (
        manager.set_nifty_real_trading_enabled(
            True
        )
    )

    return {
        "status": "SUCCESS",
        "message": "NIFTY Real Trading enabled.",
        "enabled": enabled,
    }


@router.post("/disable")
def disable_real_trading():

    manager = _get_nifty_manager()

    enabled = (
        manager.set_nifty_real_trading_enabled(
            False
        )
    )

    return {
        "status": "SUCCESS",
        "message": "NIFTY Real Trading disabled.",
        "enabled": enabled,
    }


# =========================================================
# NIFTY REAL TRADE HISTORY
# =========================================================
#
# READ ONLY.
#
# These endpoints read the existing persistent
# NiftyRealPnlStore.
#
# They do NOT:
#   - contact Angel One
#   - place orders
#   - modify positions
#   - modify P&L
#   - affect Paper Trading
#
# =========================================================


@router.get("/trades")
def get_real_trades():

    store = _get_real_pnl_store()

    payload = store.load()

    trades = payload.get("trades", [])

    if not isinstance(trades, list):
        trades = []

    trades = [
        _normalize_trade_pnl(trade)
        for trade in trades
    ]

    return {
        "status": "SUCCESS",
        "market": "NIFTY_FNO",
        "currency": "INR",
        "count": len(trades),
        "trades": trades,
    }


@router.get("/trades/today")
def get_today_real_trades():

    store = _get_real_pnl_store()

    status = store.get_status()

    trade_date = status["today"]

    payload = store.load()

    all_trades = payload.get("trades", [])

    if not isinstance(all_trades, list):
        all_trades = []

    trades = [
        _normalize_trade_pnl(trade)
        for trade in all_trades
        if str(
            trade.get("trade_date") or ""
        ) == trade_date
    ]

    return {
        "status": "SUCCESS",
        "market": "NIFTY_FNO",
        "currency": "INR",
        "trade_date": trade_date,
        "count": len(trades),
        "daily_realized_pnl": _round_pnl_value(
            status["daily_realized_pnl"]
        ),
        "trades": trades,
    }


@router.get("/pnl")
def get_real_pnl():

    store = _get_real_pnl_store()

    status = store.get_status()

    return {
        "status": "SUCCESS",
        "market": status["market"],
        "currency": status["currency"],
        "today": status["today"],
        "daily_realized_pnl": _round_pnl_value(
            status["daily_realized_pnl"]
        ),
        "cumulative_realized_pnl": _round_pnl_value(
            status["cumulative_realized_pnl"]
        ),
        "closed_trade_count": status["closed_trade_count"],
    }
