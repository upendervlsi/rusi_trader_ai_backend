"""
============================================================
RUSI Trader AI

Paper Trading API
============================================================
"""

from fastapi import APIRouter

from backend.services.paper_trading_service import (
    PaperTradingService,
)


router = APIRouter(
    prefix="/api/paper-trading",
    tags=["Paper Trading"],
)


service = PaperTradingService()


@router.post("/start")
def start_paper_trading():

    return service.start()


@router.post("/stop")
def stop_paper_trading():

    return service.stop()


@router.get("/status")
def paper_trading_status():

    return service.status()
