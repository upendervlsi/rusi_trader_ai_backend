"""
============================================================

Momentum API

============================================================
"""

from fastapi import APIRouter

from backend.services.market_data_service import (
    MarketDataService,
)

router = APIRouter(
    prefix="/api",
    tags=["Momentum"],
)

market_service = MarketDataService()


@router.get("/momentum")
def get_momentum():

    return market_service.get_momentum()
