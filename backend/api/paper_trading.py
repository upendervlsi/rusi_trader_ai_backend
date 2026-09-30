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


@router.get("/dashboard")
def paper_trading_dashboard():

    # READ ONLY:
    # Exposes existing PaperTrade records for the dashboard.
    # Does not start/stop trading, contact the broker, or modify trades.
    return service.dashboard_snapshot()
