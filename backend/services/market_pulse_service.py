"""
============================================================

RUSI Trader AI

Market Pulse Service

Provides the seven-market dashboard view.

The service is READ ONLY.

Market analysis results come from MarketPulseRuntime.

It never fabricates BUY / SELL / HOLD signals.

Execution remains completely separate.

============================================================
"""

from __future__ import annotations

from backend.models.dashboard_model import (
    MarketPulseModel,
)

from backend.services.market_pulse_runtime import (
    MarketPulseRuntime,
)


class MarketPulseService:

    """
    Dashboard-level reader for the seven market states.

    Supported markets:

        NIFTY
        BANKNIFTY
        FINNIFTY
        MIDCAP NIFTY
        SENSEX
        BANKEX
        CRUDE OIL
    """

    MARKETS = (
        {
            "id": "NIFTY_FNO",
            "name": "NIFTY",
        },
        {
            "id": "BANKNIFTY_FNO",
            "name": "BANKNIFTY",
        },
        {
            "id": "FINNIFTY_FNO",
            "name": "FINNIFTY",
        },
        {
            "id": "MIDCPNIFTY_FNO",
            "name": "MIDCAP NIFTY",
        },
        {
            "id": "SENSEX_FNO",
            "name": "SENSEX",
        },
        {
            "id": "BANKEX_FNO",
            "name": "BANKEX",
        },
        {
            "id": "CRUDEOIL_FNO",
            "name": "CRUDE OIL",
        },
    )

    def __init__(self):

        self._runtime = (
            MarketPulseRuntime()
        )

    # ---------------------------------------------------------
    # Dashboard Pulse
    # ---------------------------------------------------------

    def get_market_pulse(
        self,
        updated_time: str,
    ) -> list[MarketPulseModel]:

        result = []

        for market in self.MARKETS:

            state = self._runtime.get(
                market["id"]
            )

            result.append(

                MarketPulseModel(

                    market=state.market,

                    display_name=state.display_name,

                    signal=state.signal,

                    confidence=state.confidence,

                    status=state.status,

                    updated_time=(
                        state.updated_time
                        or updated_time
                    ),

                    symbol=state.symbol,

                    exchange=state.exchange,

                    last_price=state.last_price,

                    trend=state.trend,

                    score=state.score,

                    reason=state.reason,
                )
            )

        return result

    # ---------------------------------------------------------
    # Strongest Market
    # ---------------------------------------------------------

    def strongest_market(
        self,
        pulse: list[MarketPulseModel],
    ) -> tuple[str | None, float | None]:

        valid = [

            item

            for item in pulse

            if item.confidence is not None
            and item.status.upper() != "WAITING"
        ]

        if not valid:

            return None, None

        strongest = max(

            valid,

            key=lambda item:
                item.confidence
                if item.confidence is not None
                else -1,
        )

        return (
            strongest.display_name,
            strongest.confidence,
        )
