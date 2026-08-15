"""
============================================================
RUSI Trader AI

Market Selection API

Allows the Flutter dashboard to select the active market.
============================================================
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.trading_engine_service import (
    TradingEngineService,
)

router = APIRouter(
    prefix="/api",
    tags=["Market Selection"],
)


class MarketSelectionRequest(BaseModel):

    market: str


@router.get("/markets")
def get_markets():

    return {
        "markets": [
            "NIFTY_FNO",
            "BANKNIFTY_FNO",
            "FINNIFTY_FNO",
            "MIDCPNIFTY_FNO",
            "SENSEX_FNO",
            "BANKEX_FNO",
        ]
    }


@router.post("/market/select")
def select_market(
    request: MarketSelectionRequest,
):

    service = TradingEngineService()

    try:

        instrument = service.select_market(
            request.market
        )

        return {
            "status": "SUCCESS",
            "selected_market": request.market,
            "symbol": instrument.symbol,
            "exchange": instrument.exchange,
            "token": instrument.token,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )
