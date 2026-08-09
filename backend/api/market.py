"""
============================================================

RUSI Trader AI

Market API

Provides market information to Flutter.

Author : RUSI Trader AI

============================================================
"""

from fastapi import APIRouter

from backend.services.market_service import (
    MarketService,
)

router = APIRouter(
    prefix="/api",
    tags=["Market"],
)

_service = MarketService()


@router.get(
    "/market",
)
def get_market():
    """
    Returns the latest market information.

    Data Source

        ExecutionManager

            ↓

        RuntimeManager

            ↓

        TradingEngineFacade

            ↓

        MarketService

            ↓

        REST API
    """

    return _service.get_market()
