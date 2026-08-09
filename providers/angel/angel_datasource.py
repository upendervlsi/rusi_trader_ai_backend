"""
=============================================================
RUSI Trader AI

Angel Market Data Source

Provides historical and current market data for the
resolved TradingInstrument.

=============================================================
"""

from __future__ import annotations

from trading.context.trading_context import (
    TradingInstrument,
)


class AngelDataSource:

    """
    Angel One market-data provider.

    The datasource does not own instrument definitions.

    It always uses the fully resolved TradingInstrument
    supplied during construction.
    """

    def __init__(
        self,
        client,
        instrument: TradingInstrument,
    ):

        self._client = client

        self._instrument = instrument

        self._print_selected()

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def instrument(self):

        return self._instrument

    # ---------------------------------------------------------
    # Debug
    # ---------------------------------------------------------

    def _print_selected(self):

        print()

        print("=" * 60)

        print("Angel Data Source")

        print("=" * 60)

        print("Resolved Instrument")

        print("------------------------------")

        print(
            f"Symbol   : "
            f"{self._instrument.symbol}"
        )

        print(
            f"Exchange : "
            f"{self._instrument.exchange}"
        )

        print(
            f"Token    : "
            f"{self._instrument.token}"
        )

        print("=" * 60)

    # ---------------------------------------------------------
    # Historical Data
    # ---------------------------------------------------------

    def get_historical_data(
        self,
        exchange=None,
        token=None,
        interval="FIVE_MINUTE",
        from_datetime=None,
        to_datetime=None,
    ):
        """
        Historical data wrapper.

        If exchange/token are omitted, the resolved
        TradingInstrument is used.
        """

        exchange = (
            exchange
            or self._instrument.exchange
        )

        token = (
            token
            or self._instrument.token
        )

        return self._client.get_historical_data(
            exchange=exchange,
            token=token,
            interval=interval,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
        )

    # ---------------------------------------------------------
    # Live LTP
    # ---------------------------------------------------------

    def get_ltp(
        self,
        exchange=None,
        symbol=None,
        token=None,
    ):
        """
        Get the latest traded price.

        Defaults to the resolved TradingInstrument.
        """

        exchange = (
            exchange
            or self._instrument.exchange
        )

        symbol = (
            symbol
            or self._instrument.symbol
        )

        token = (
            token
            or self._instrument.token
        )

        return self._client.get_ltp(
            exchange=exchange,
            trading_symbol=symbol,
            symbol_token=token,
        )

    # ---------------------------------------------------------
    # Market Quote
    # ---------------------------------------------------------

    def get_quote(
        self,
        exchange=None,
        token=None,
    ):
        """
        Get richer quote information.

        Defaults to the resolved TradingInstrument.
        """

        exchange = (
            exchange
            or self._instrument.exchange
        )

        token = (
            token
            or self._instrument.token
        )

        return self._client.get_quote(
            exchange=exchange,
            symbol_token=token,
        )
