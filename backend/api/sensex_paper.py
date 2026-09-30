"""
SENSEX Paper Trading API

Read-only dashboard endpoint for the isolated SENSEX paper
trading service.

This router does NOT place orders, modify positions, or control
the SENSEX scheduler.
"""

from fastapi import APIRouter

from backend.services.sensex_paper_trading_service import (
    SensexPaperTradingService,
)


router = APIRouter(
    prefix="/api/sensex/paper",
    tags=["SENSEX Paper"],
)


# One service instance for read-only status access.
service = SensexPaperTradingService()


@router.get("/status")
def get_sensex_paper_status():
    """
    Return the isolated SENSEX paper-trading state.

    Read-only:
      - no order placement
      - no position modification
      - no scheduler control
      - no real execution
    """
    return service.status()
