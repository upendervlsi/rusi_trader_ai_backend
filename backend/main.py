"""
=========================================================

RUSI Trader AI Backend

FastAPI Entry Point

=========================================================
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.health import router as health_router
from backend.api.dashboard import router as dashboard_router
from backend.api.market import router as market_router
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
from backend.services.trading_engine_service import (
    TradingEngineService,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    #
    # Start Trading Engine
    #

    TradingEngineService().start()

    yield

    #
    # Future
    #
    # TradingEngineService().stop()
    #


app = FastAPI(

    title="RUSI Trader AI Backend",

    version="1.0.0",

    description="REST API for RUSI Trader AI",

    lifespan=lifespan,

)

from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()

    print("\n" + "=" * 70)
    print(f"REQUEST : {request.method} {request.url}")
    print(f"CLIENT  : {request.client.host}")

    response = await call_next(request)

    duration = (time.time() - start) * 1000

    print(f"STATUS  : {response.status_code}")
    print(f"TIME    : {duration:.2f} ms")
    print("=" * 70)

    return response

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)

#
# APIs
#

app.include_router(health_router)

app.include_router(dashboard_router)

app.include_router(market_router)

app.include_router(recommendation_router)

app.include_router(portfolio_router)

app.include_router(indicators_router)

app.include_router(momentum_router)

app.include_router(options_router)

app.include_router(intelligence_router)

@app.get("/")
def root():

    return {

        "application": "RUSI Trader AI",

        "status": "RUNNING",

        "version": "1.0.0",

    }
