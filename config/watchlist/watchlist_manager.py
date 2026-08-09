"""
=============================================================
RUSI Trader AI

Watchlist Manager

Provides logical trading instruments.

Broker specific token resolution is performed later by the
Instrument Resolver.

Sprint-17
=============================================================
"""

from __future__ import annotations

import json

from pathlib import Path

from trading.context.trading_context import TradingInstrument


class WatchlistManager:

    def __init__(self):

        self._watchlist_file = (
            Path(__file__).parent / "watchlist.json"
        )

        self._watchlist = self._load()

    # ---------------------------------------------------------
    # Private
    # ---------------------------------------------------------

    def _load(self):

        with self._watchlist_file.open(
            "r",
            encoding="utf-8",
        ) as fp:

            return json.load(fp)

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    @property
    def default_market(self):

        return self._watchlist["default_market"]

    def current(self) -> TradingInstrument:

        return self.get(
            self.default_market
        )

    def get(
        self,
        market_name: str,
    ) -> TradingInstrument:

        markets = self._watchlist["markets"]

        if market_name not in markets:

            raise ValueError(
                f"Unknown market: {market_name}"
            )

        item = markets[market_name]

        #
        # Logical instrument only.
        #
        # Token will be resolved later.
        #

        return TradingInstrument(

            symbol=item["symbol"],

            exchange=item["exchange"],

            token=item.get(
                "token",
                "",
            ),

            quantity=item.get(
                "quantity",
                1,
            ),

            order_type=item.get(
                "order_type",
                "MARKET",
            ),

            product_type=item.get(
                "product_type",
                "INTRADAY",
            ),
        )

    def markets(self):

        return sorted(
            self._watchlist["markets"].keys()
        )

    def exists(
        self,
        market_name: str,
    ) -> bool:

        return (
            market_name
            in self._watchlist["markets"]
        )

    def summary(self):

        print()

        print("=" * 60)
        print("Watchlist Summary")
        print("=" * 60)

        print(
            "Default Market :",
            self.default_market,
        )

        print()

        for market in self.markets():

            instrument = self.get(market)

            print(
                f"{market:<20}"
                f"{instrument.symbol:<15}"
                f"{instrument.exchange:<8}"
            )

        print("=" * 60)
