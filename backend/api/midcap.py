"""
============================================================
RUSI Trader AI

MIDCAP Runtime API

Dedicated read-only API for MIDCPNIFTY_FNO.

This API reads ONLY the isolated MIDCAP runtime state.

It does NOT modify:
    - existing NIFTY V1 APIs
    - default RuntimeManager.state
    - market selection
    - trading strategy
    - execution logic
============================================================
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from trading.runtime.runtime_manager import RuntimeManager
from backend.services.market_session_service import MarketSessionService


router = APIRouter(
    prefix="/api/midcap",
    tags=["MIDCAP"],
)


MARKET_NAME = "MIDCPNIFTY_FNO"


# ============================================================
# PERSISTENT P&L
# ============================================================

TRADE_JOURNAL_FILE = (
    Path(__file__).resolve().parents[2]
    / "runs"
    / "trade_journal.csv"
)

IST = ZoneInfo("Asia/Kolkata")


def _journal_exit_time_ist(value):
    """
    Convert journal ExitTime to IST.

    Journal timestamps may be timezone-aware or naive.
    Naive timestamps are treated as UTC because the backend
    journal is generated from the server/runtime timestamps.
    """

    if not value:
        return None

    try:
        dt = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(IST)

    except (TypeError, ValueError):
        return None


@router.get("/pnl")
def get_midcap_pnl():
    """
    Return persistent MIDCAP realized P&L from trade journal.

    This endpoint intentionally does NOT depend on the runtime
    portfolio state, so P&L remains available after market close
    and after the runtime clears its active positions.
    """

    today = datetime.now(IST).date()

    cumulative_realized_pnl = 0.0
    today_realized_pnl = 0.0

    cumulative_wins = 0
    cumulative_losses = 0

    today_wins = 0
    today_losses = 0

    cumulative_closed_trades = 0
    today_closed_trades = 0

    if not TRADE_JOURNAL_FILE.exists():
        return {
            "market": MARKET_NAME,
            "date": today.isoformat(),
            "starting_capital": 100000.0,
            "today_realized_pnl": 0.0,
            "cumulative_realized_pnl": 0.0,
            "today_closed_trades": 0,
            "today_wins": 0,
            "today_losses": 0,
            "cumulative_closed_trades": 0,
            "cumulative_wins": 0,
            "cumulative_losses": 0,
            "data_status": "JOURNAL_NOT_FOUND",
        }

    with TRADE_JOURNAL_FILE.open(
        newline="",
        encoding="utf-8",
    ) as f:

        for row in csv.DictReader(f):
            symbol = (
                row.get("Symbol") or ""
            ).upper()

            status = (
                row.get("Status") or ""
            ).upper()

            if not symbol.startswith("MIDCPNIFTY"):
                continue

            if status != "CLOSED":
                continue

            try:
                pnl = float(
                    row.get("RealizedPnL") or 0.0
                )
            except (TypeError, ValueError):
                continue

            exit_time = _journal_exit_time_ist(
                row.get("ExitTime")
            )

            if exit_time is None:
                continue

            cumulative_realized_pnl += pnl
            cumulative_closed_trades += 1

            if pnl > 0:
                cumulative_wins += 1
            elif pnl < 0:
                cumulative_losses += 1

            if exit_time.date() == today:
                today_realized_pnl += pnl
                today_closed_trades += 1

                if pnl > 0:
                    today_wins += 1
                elif pnl < 0:
                    today_losses += 1

    return {
        "market": MARKET_NAME,
        "date": today.isoformat(),
        "starting_capital": 100000.0,
        "today_realized_pnl": round(
            today_realized_pnl,
            2,
        ),
        "cumulative_realized_pnl": round(
            cumulative_realized_pnl,
            2,
        ),
        "today_closed_trades": today_closed_trades,
        "today_wins": today_wins,
        "today_losses": today_losses,
        "cumulative_closed_trades": cumulative_closed_trades,
        "cumulative_wins": cumulative_wins,
        "cumulative_losses": cumulative_losses,
        "data_status": "PERSISTED",
    }


def _get_midcap_state():
    """
    Return the isolated MIDCAP runtime state.

    The runtime state is published by ExecutionManager
    through RuntimeManager.update_for_market().
    """

    runtime = RuntimeManager()

    return runtime.get_state_for_market(
        MARKET_NAME
    )


def _state_value(state, name, default=None):
    """
    Safely read a runtime-state field.
    """

    return getattr(
        state,
        name,
        default,
    )


# ============================================================
# MARKET
# ============================================================

@router.get("/market")
def get_midcap_market():
    """
    Return the isolated MIDCAP market snapshot.
    """

    state = _get_midcap_state()

    snapshot = _state_value(
        state,
        "snapshot",
    )

    if snapshot is None:
        raise HTTPException(
            status_code=503,
            detail="MIDCAP runtime data is not available yet.",
        )

    return jsonable_encoder(
        {
            "market": MARKET_NAME,
            "cycle_id": _state_value(
                state,
                "cycle_id",
                0,
            ),
            "updated_time": _state_value(
                state,
                "updated_time",
                "",
            ),
            "data_status": _state_value(
                state,
                "data_status",
                "UNKNOWN",
            ),
            "live_price": _state_value(
                state,
                "live_price",
                None,
            ),
            "instrument": _state_value(
                state,
                "instrument",
                None,
            ),
            "snapshot": snapshot,
        }
    )


# ============================================================
# INDICATORS
# ============================================================

@router.get("/indicators")
def get_midcap_indicators():
    """
    Return indicators from the isolated MIDCAP snapshot.
    """

    state = _get_midcap_state()

    snapshot = _state_value(
        state,
        "snapshot",
    )

    if snapshot is None:
        raise HTTPException(
            status_code=503,
            detail="MIDCAP runtime data is not available yet.",
        )

    indicators = getattr(
        snapshot,
        "indicators",
        None,
    )

    if indicators is None:
        raise HTTPException(
            status_code=503,
            detail="MIDCAP indicators are not available yet.",
        )

    return jsonable_encoder(
        {
            "market": MARKET_NAME,
            "cycle_id": _state_value(
                state,
                "cycle_id",
                0,
            ),
            "updated_time": _state_value(
                state,
                "updated_time",
                "",
            ),
            "data_status": _state_value(
                state,
                "data_status",
                "UNKNOWN",
            ),
            "indicators": indicators,
        }
    )


# ============================================================
# MOMENTUM
# ============================================================

@router.get("/momentum")
def get_midcap_momentum():
    """
    Return momentum indicators from the isolated
    MIDCAP runtime snapshot.
    """

    state = _get_midcap_state()

    snapshot = _state_value(
        state,
        "snapshot",
    )

    if snapshot is None:
        raise HTTPException(
            status_code=503,
            detail="MIDCAP runtime data is not available yet.",
        )

    indicators = getattr(
        snapshot,
        "indicators",
        None,
    )

    if indicators is None:
        raise HTTPException(
            status_code=503,
            detail="MIDCAP indicators are not available yet.",
        )

    return jsonable_encoder(
        {
            "market": MARKET_NAME,
            "cycle_id": _state_value(
                state,
                "cycle_id",
                0,
            ),
            "updated_time": _state_value(
                state,
                "updated_time",
                "",
            ),
            "data_status": _state_value(
                state,
                "data_status",
                "UNKNOWN",
            ),
            "rsi": getattr(
                indicators,
                "rsi14",
                0.0,
            ),
            "macd": getattr(
                indicators,
                "macd",
                0.0,
            ),
            "adx": getattr(
                indicators,
                "adx14",
                0.0,
            ),
            "atr": getattr(
                indicators,
                "atr14",
                0.0,
            ),
        }
    )


# ============================================================
# OPTIONS
# ============================================================

@router.get("/options")
def get_midcap_options():
    """
    Return option analytics from the isolated MIDCAP
    runtime snapshot.
    """

    state = _get_midcap_state()

    snapshot = _state_value(
        state,
        "snapshot",
    )

    if snapshot is None:
        raise HTTPException(
            status_code=503,
            detail="MIDCAP runtime data is not available yet.",
        )

    analysis = getattr(
        snapshot,
        "analysis",
        None,
    )

    options = getattr(
        analysis,
        "options",
        None,
    ) if analysis is not None else None

    return jsonable_encoder(
        {
            "market": MARKET_NAME,
            "cycle_id": _state_value(
                state,
                "cycle_id",
                0,
            ),
            "updated_time": _state_value(
                state,
                "updated_time",
                "",
            ),
            "data_status": _state_value(
                state,
                "data_status",
                "UNKNOWN",
            ),
            "options": options,
        }
    )


# ============================================================
# RECOMMENDATION
# ============================================================

@router.get("/recommendation")
def get_midcap_recommendation():
    """
    Return the isolated MIDCAP recommendation.
    """

    state = _get_midcap_state()

    recommendation = _state_value(
        state,
        "recommendation",
    )

    if recommendation is None:
        decision = _state_value(
            state,
            "decision",
            None,
        )

        return jsonable_encoder(
            {
                "market": MARKET_NAME,
                "cycle_id": _state_value(
                    state,
                    "cycle_id",
                    0,
                ),
                "updated_time": _state_value(
                    state,
                    "updated_time",
                    "",
                ),
                "data_status": _state_value(
                    state,
                    "data_status",
                    "UNKNOWN",
                ),
                "recommendation": None,
                "decision": decision,
                "execution_allowed": False,
                "status": "DECISION_AVAILABLE_NOT_EXECUTABLE",
            }
        )

    return jsonable_encoder(
        {
            "market": MARKET_NAME,
            "cycle_id": _state_value(
                state,
                "cycle_id",
                0,
            ),
            "updated_time": _state_value(
                state,
                "updated_time",
                "",
            ),
            "data_status": _state_value(
                state,
                "data_status",
                "UNKNOWN",
            ),
            "recommendation": recommendation,
        }
    )


# ============================================================
# COMPLETE RUNTIME
# ============================================================

@router.get("/runtime")
def get_midcap_runtime():
    """
    Return the complete isolated MIDCAP runtime state.

    This endpoint is primarily for the MIDCAP dashboard
    and debugging/observation.
    """

    state = _get_midcap_state()

    # ---------------------------------------------------------
    # Market Session Status
    # ---------------------------------------------------------
    # Market status is derived from the authoritative
    # MarketSessionService using the isolated MIDCAP
    # runtime instrument exchange.
    # ---------------------------------------------------------

    session_service = MarketSessionService()

    instrument = _state_value(
        state,
        "instrument",
        None,
    )

    exchange = (
        getattr(
            instrument,
            "exchange",
            None,
        )
        if instrument is not None
        else None
    )

    market_status = (
        session_service.get_market_status(
            exchange
        )
        if exchange
        else "CLOSED"
    )

    market_open = (
        market_status == "OPEN"
    )

    return jsonable_encoder(
        {
            "market": MARKET_NAME,
            "market_status": market_status,
            "market_open": market_open,
            "cycle_id": _state_value(
                state,
                "cycle_id",
                0,
            ),
            "updated_time": _state_value(
                state,
                "updated_time",
                "",
            ),
            "data_status": _state_value(
                state,
                "data_status",
                "UNKNOWN",
            ),
            "snapshot": _state_value(
                state,
                "snapshot",
                None,
            ),
            "instrument": _state_value(
                state,
                "instrument",
                None,
            ),
            "live_price": _state_value(
                state,
                "live_price",
                None,
            ),
            "option_live_price": _state_value(
                state,
                "option_live_price",
                None,
            ),
            "feature_store": _state_value(
                state,
                "feature_store",
                None,
            ),
            "evidence": _state_value(
                state,
                "evidence",
                None,
            ),
            "intelligence": _state_value(
                state,
                "intelligence",
                None,
            ),
            "decision": _state_value(
                state,
                "decision",
                None,
            ),
            "recommendation": _state_value(
                state,
                "recommendation",
                None,
            ),
            "execution_policy": _state_value(
                state,
                "execution_policy",
                None,
            ),

            # -------------------------------------------------
            # PAPER TRADING POSITION
            # -------------------------------------------------
            # Expose the authoritative PositionManager state
            # to the MIDCAP dashboard.
            #
            "position": _state_value(
                state,
                "position",
                None,
            ),

            "positions": _state_value(
                state,
                "positions",
                [],
            ),

            # -------------------------------------------------
            # PORTFOLIO
            # -------------------------------------------------
            "portfolio": _state_value(
                state,
                "portfolio",
                None,
            ),

            "portfolio_summary": _state_value(
                state,
                "portfolio_summary",
                None,
            ),
        }
    )
