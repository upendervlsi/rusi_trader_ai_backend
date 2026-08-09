"""
============================================================

Option Analytics API

============================================================
"""

from fastapi import APIRouter

from backend.services.market_data_service import (
    MarketDataService,
)

router = APIRouter(
    prefix="/api",
    tags=["Options"],
)

market_service = MarketDataService()


@router.get("/options")
def get_options():

    return market_service.get_options()
