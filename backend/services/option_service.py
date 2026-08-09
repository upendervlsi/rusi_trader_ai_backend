"""
============================================================

RUSI Trader AI

Option Service

Responsible for option analytics.

============================================================
"""

from backend.services.models.market_snapshot import (
    MarketSnapshot,
)


class OptionService:

    """
    Updates all option related analytics.
    """

    def update(
        self,
        snapshot: MarketSnapshot,
    ) -> None:

        #
        # TODO
        #
        # Replace with actual option chain calculations.
        #

        snapshot.pcr = 1.14

        snapshot.open_interest = 2450000

        snapshot.change_oi = 142500

        snapshot.implied_volatility = 12.40

        snapshot.max_pain = 24400
