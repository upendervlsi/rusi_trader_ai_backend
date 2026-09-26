"""
RUSI Trader AI

Stock Options Observation API

Stage 9B

Read-only API for the Stock Options observation module.
This API is isolated from the existing NIFTY V1 APIs.
"""

from __future__ import annotations

import csv
from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.services.stock_options_paper_trading_service import (
    StockOptionsPaperTradingService,
)


router = APIRouter(
    prefix="/api/stock-options",
    tags=["Stock Options"],
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

paper_trading_service = (
    StockOptionsPaperTradingService()
)

stock_options_paper_trading_service = (
    paper_trading_service
)


OBSERVATION_FILE = (
    PROJECT_ROOT
    / "runs"
    / "stock_options"
    / "observations.csv"
)


def _read_observations() -> list[dict]:
    if not OBSERVATION_FILE.exists():
        return []

    with OBSERVATION_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as fp:
        return list(csv.DictReader(fp))


def _latest_by_symbol(
    observations: list[dict],
) -> dict[str, dict]:
    latest: dict[str, dict] = {}

    for observation in observations:
        symbol = observation.get("Symbol")

        if not symbol:
            continue

        latest[symbol] = observation

    return latest


@router.get("/summary")
def get_stock_options_summary():
    observations = _read_observations()
    latest = _latest_by_symbol(observations)

    candidate_count = sum(
        1
        for observation in latest.values()
        if observation.get("Decision") == "CANDIDATE"
    )

    no_trade_count = sum(
        1
        for observation in latest.values()
        if observation.get("Decision") == "NO_TRADE"
    )

    risk_allowed_count = 0
    risk_rejected_count = 0

    for observation in latest.values():
        metadata = observation.get("Metadata", "")

        if '"risk_allowed":true' in metadata:
            risk_allowed_count += 1
        elif '"risk_allowed":false' in metadata:
            risk_rejected_count += 1

    return {
        "stocks_observed": len(latest),
        "observations": len(observations),
        "candidates": candidate_count,
        "no_trade": no_trade_count,
        "risk_allowed": risk_allowed_count,
        "risk_rejected": risk_rejected_count,
        "observation_file": str(OBSERVATION_FILE),
    }


@router.get("/candidates")
def get_stock_options_candidates():
    """
    Return the latest candidate observation for each
    observed stock.

    This endpoint intentionally retains the broader
    observation dataset. It is not the Current Top-3 endpoint.
    """

    observations = _read_observations()
    latest = _latest_by_symbol(observations)

    candidates = [
        observation
        for observation in latest.values()
        if observation.get("Decision") == "CANDIDATE"
    ]

    candidates.sort(
        key=lambda item: float(
            item.get("QualityScore") or 0
        ),
        reverse=True,
    )

    return {
        "count": len(candidates),
        "candidates": candidates,
    }


@router.get("/top")
def get_stock_options_top():
    """
    Return the current Top-3 Stock Options candidates.

    The Stock Options scheduler refreshes observations
    specifically for the current Top-3 before a new
    paper-entry decision.

    Therefore, the three most recently observed candidate
    records represent the current active Top-3.
    """

    observations = _read_observations()
    latest = _latest_by_symbol(observations)

    candidates = [
        observation
        for observation in latest.values()
        if observation.get("Decision") == "CANDIDATE"
    ]

    candidates.sort(
        key=lambda item: item.get("ObservedAt") or "",
        reverse=True,
    )

    top_candidates = candidates[:3]

    return {
        "count": len(top_candidates),
        "candidates": top_candidates,
    }


@router.get("/observations")
def get_stock_options_observations():
    observations = _read_observations()

    return {
        "count": len(observations),
        "observations": observations,
    }


# ============================================================
# STOCK OPTIONS PAPER TRADING
# ============================================================

@router.post("/paper-trade/top")
def paper_trade_top_stock_option():
    """
    Execute the current highest-quality eligible
    Stock Options candidate in PAPER mode.

    The service performs fresh quote and risk validation
    before paper execution.
    """

    return paper_trading_service.paper_trade_top()


@router.get("/paper-trade/status")
def stock_options_paper_trade_status():
    """Return the independent Stock Options paper portfolio."""

    return paper_trading_service.status()


@router.post("/paper-trade/monitor")
def monitor_stock_option_position():
    """
    Monitor the currently open Stock Options paper position.

    Uses a fresh option quote and applies the independent
    Stock Options position-monitoring and exit logic.
    """

    return paper_trading_service.monitor_open_position()


@router.post("/paper-trade/close")
def close_stock_option_paper_position():
    """
    Administrative PAPER-only close.

    No real broker order is submitted.
    """

    return (
        paper_trading_service
        .close_paper_position_admin()
    )


# ============================================================
# STOCK OPTIONS TRADE MAP
# ============================================================

@router.get("/trade-map")
def get_stock_options_trade_map():
    """
    Return Stock Options paper-trade history for the Trade Map.

    This endpoint is read-only. It does not modify the paper
    portfolio, submit orders, or affect the scheduler.
    """

    paper_trading_service._load_trade_history()

    history = list(
        paper_trading_service._trade_history
    )

    status = paper_trading_service.status()

    positions = status.get("positions", [])

    open_position = (
        positions[0]
        if positions
        else None
    )

    current_trade_number = None

    if open_position:
        metadata = (
            open_position.get("metadata")
            or {}
        )

        current_trade_number = metadata.get(
            "trade_number"
        )

        if current_trade_number is None:
            position_symbol = open_position.get(
                "symbol"
            )

            matching_events = [
                event
                for event in history
                if event.get("symbol")
                == position_symbol
                and event.get("trade_number")
                is not None
            ]

            if matching_events:
                current_trade_number = max(
                    int(
                        event["trade_number"]
                    )
                    for event in matching_events
                )

    return {
        "success": True,
        "current_trade_number": current_trade_number,
        "open_position": open_position,
        "event_count": len(history),
        "events": history,
    }


@router.get("/{symbol}")
def get_stock_option_symbol(symbol: str):
    observations = _read_observations()

    matches = [
        observation
        for observation in observations
        if observation.get("Symbol") == symbol.upper()
    ]

    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No observation found for {symbol.upper()}",
        )

    return {
        "symbol": symbol.upper(),
        "observations": matches,
    }
