"""
============================================================

Indicator Service

Responsible only for technical indicators.

============================================================
"""

from backend.services.models.market_snapshot import (
    MarketSnapshot,
)


class IndicatorService:

    def update(
        self,
        snapshot: MarketSnapshot,
    ) -> None:

        #
        # TODO
        #
        # Replace these with real calculations.
        #

        snapshot.ema20 = 24382.15

        snapshot.ema50 = 24340.80

        snapshot.sma20 = 24376.20

        snapshot.sma50 = 24318.50

        snapshot.vwap = 24370.10
