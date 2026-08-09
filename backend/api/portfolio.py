"""
============================================================

Portfolio API

============================================================
"""

from fastapi import APIRouter

from backend.services.portfolio_service import (
    PortfolioService,
)

router = APIRouter(
    prefix="/api",
    tags=["Portfolio"],
)

service = PortfolioService()


@router.get("/portfolio")
def portfolio():

    return service.get_portfolio()
