"""
============================================================

Momentum Service

Responsible for momentum indicators.

============================================================
"""


from backend.services.models.market_snapshot import (
    MarketSnapshot,
)

class MomentumService:

    def update(
        self,
        snapshot: MarketSnapshot,
    ) -> None:

        #
        # TODO
        #
        # Replace with real calculations.
        #

        snapshot.rsi = 61.25

        snapshot.macd = 14.62

        snapshot.adx = 28.15

        snapshot.atr = 96.40
