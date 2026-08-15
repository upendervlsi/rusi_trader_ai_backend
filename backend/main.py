"""
=========================================================

RUSI Trader AI Backend

FastAPI Entry Point

=========================================================
"""

from contextlib import asynccontextmanager

import time

from fastapi import FastAPI
from fastapi import Request

from fastapi.middleware.cors import CORSMiddleware

from backend.api.health import (
    router as health_router,
)

from backend.api.dashboard import (
    router as dashboard_router,
)

from backend.api.market import (
    router as market_router,
)

from backend.api.market_selection import (
    router as market_selection_router,
)

from backend.api.recommendation import (
    router as recommendation_router,
)

from backend.api.portfolio import (
    router as portfolio_router,
)

from backend.api.indicators import (
    router as indicators_router,
)

from backend.api.momentum import (
    router as momentum_router,
)

from backend.api.options import (
    router as options_router,
)

from backend.api.intelligence_api import (
    router as intelligence_router,
)

from backend.api.suggestions import (
    router as suggestions_router,
)

from backend.services.trading_engine_service import (
    TradingEngineService,
)

from backend.services.market_pulse_scanner_service import (
    MarketPulseScannerService,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    #
    # =========================================================
    # RUSI TRADING ENGINE
    # =========================================================
    #

    TradingEngineService().start()

    #
    # =========================================================
    # MARKET PULSE SCANNER
    # =========================================================
    #
    # Independent from the execution engine.
    #
    # It analyzes:
    #
    #   NIFTY
    #   BANKNIFTY
    #   FINNIFTY
    #   MIDCAP NIFTY
    #   SENSEX
    #   BANKEX
    #   CRUDE OIL
    #
    # The analyzer itself intentionally keeps CRUDE OIL
    # waiting until the real MCX option-analysis path exists.
    #

    MarketPulseScannerService().start()

    yield

    #
    # =========================================================
    # SHUTDOWN
    # =========================================================
    #

    MarketPulseScannerService().stop()

    TradingEngineService().stop()


app = FastAPI(

    title="RUSI Trader AI Backend",

    version="1.0.0",

    description="REST API for RUSI Trader AI",

    lifespan=lifespan,

)


# =========================================================
# REQUEST LOGGING
# =========================================================

@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):

    start = time.time()

    print(
        "\n"
        + "=" * 70
    )

    print(
        f"REQUEST : {request.method} {request.url}"
    )

    if request.client is not None:

        print(
            f"CLIENT  : {request.client.host}"
        )

    response = await call_next(
        request
    )

    duration = (
        time.time()
        - start
    ) * 1000

    print(
        f"STATUS  : {response.status_code}"
    )

    print(
        f"TIME    : {duration:.2f} ms"
    )

    print(
        "=" * 70
    )

    return response


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# =========================================================
# APIs
# =========================================================

app.include_router(
    health_router
)

app.include_router(
    dashboard_router
)

app.include_router(
    market_router
)

app.include_router(
    market_selection_router
)

app.include_router(
    recommendation_router
)

app.include_router(
    portfolio_router
)

app.include_router(
    indicators_router
)

app.include_router(
    momentum_router
)

app.include_router(
    options_router
)

app.include_router(
    intelligence_router
)

app.include_router(
    suggestions_router
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {

        "application":
            "RUSI Trader AI",

        "status":
            "RUNNING",

        "version":
            "1.0.0",

    }
