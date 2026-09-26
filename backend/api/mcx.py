"""
RUSI Trader AI - MCX API.

MCX-only API layer.

Responsibilities:
    - Market data
    - Recent candle data
    - MCX intelligence
    - Read-only paper performance

Execution remains disabled.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.mcx.mcx_service import McxService
from backend.mcx.mcx_paper_performance import (
    build_performance,
)


router = APIRouter(
    prefix="/api/mcx",
    tags=["MCX"],
)

_service = McxService()


@router.get("/market")
def get_mcx_market():
    try:
        return _service.get_market()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MCX market data unavailable: "
                f"{exc}"
            ),
        ) from exc


@router.get("/candles/{key}")
def get_mcx_candles(
    key: str,
):
    try:
        return _service.get_candles(
            key=key,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MCX candle data unavailable: "
                f"{exc}"
            ),
        ) from exc


@router.get("/intelligence")
def get_mcx_intelligence():
    try:
        return _service.get_intelligence()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MCX intelligence unavailable: "
                f"{exc}"
            ),
        ) from exc


@router.get("/paper")
def get_mcx_paper_performance():
    """
    Return read-only MCX paper-trading
    performance and trade history.

    This endpoint:
        - reads local paper state
        - reads persisted observations
        - calculates statistics

    It does NOT:
        - submit orders
        - create paper trades
        - modify positions
        - modify strategy
        - modify other markets
    """

    try:
        return build_performance()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MCX paper performance unavailable: "
                f"{exc}"
            ),
        ) from exc
