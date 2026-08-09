"""
=============================================================
RUSI Trader AI

Instrument Resolver

Resolves logical trading instruments into broker instruments.

Sprint-17
=============================================================
"""

from __future__ import annotations

from trading.context.trading_context import TradingInstrument

from .instrument_master_manager import InstrumentMasterManager
from .instrument_master_parser import InstrumentMasterParser
from datetime import datetime

class InstrumentResolver:
    """
    Resolve logical instruments into broker instruments.

    Current Sprint:
        • Cash / Index resolution

    Future Sprint:
        • Futures resolution
        • Options resolution
        • Auto expiry selection
        • ATM / ITM / OTM selection
    """

    def __init__(self):

        manager = InstrumentMasterManager()

        parser = InstrumentMasterParser()

        parser.load(
            manager.load_master()
        )

        self._parser = parser

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def resolve(
        self,
        instrument: TradingInstrument,
    ) -> TradingInstrument:

        #
        # Already resolved
        #

        if instrument.token:

            return instrument

        exchange = instrument.exchange.upper()

        resolver_map = {

            "NSE": self._resolve_nse,

            "NFO": self._resolve_nfo,

            "MCX": self._resolve_mcx,

        }

        resolver = resolver_map.get(exchange)

        if resolver:

            return resolver(instrument)

        return instrument
    # ---------------------------------------------------------
    # NSE Resolution
    # ---------------------------------------------------------

    def _resolve_nse(
        self,
        instrument: TradingInstrument,
    ) -> TradingInstrument:

        matches = self._parser.get_by_exchange_symbol(
            "NSE",
            instrument.symbol,
        )

        if not matches:

            raise RuntimeError(
                f"Unable to resolve {instrument.symbol}"
            )

        #
        # Prefer exact symbol match (e.g. NIFTY token 26000)
        #

        selected = None

        for record in matches:

            if (
                record["display_symbol"].upper()
                == instrument.symbol.upper()
            ):

                selected = record
                break

        if selected is None:

            selected = matches[0]

        return TradingInstrument(
            symbol=instrument.symbol,
            exchange="NSE",
            token=selected["token"],
            quantity=instrument.quantity,
            order_type=instrument.order_type,
            product_type=instrument.product_type,
        )

    # ---------------------------------------------------------
    # Debug
    # ---------------------------------------------------------

    def print_resolution(
        self,
        instrument: TradingInstrument,
    ):

        print("=" * 60)
        print("Instrument Resolver")
        print("=" * 60)
        print("Symbol   :", instrument.symbol)
        print("Exchange :", instrument.exchange)
        print("Token    :", instrument.token)
        print("=" * 60)
    def _resolve_nfo(
        self,
        instrument: TradingInstrument,
    ) -> TradingInstrument:
        """
        Resolve the nearest NFO futures contract.
        """

        contracts = self._parser.get_nfo_futures(
            instrument.symbol
        )

        if not contracts:
            raise RuntimeError(
                f"No futures contract found for {instrument.symbol}"
            )

        contracts.sort(
            key=lambda x: datetime.strptime(
                x["expiry"],
                "%d%b%Y",
            )
        )

        selected = contracts[0]

        return TradingInstrument(
            symbol=selected["display_symbol"],
            exchange="NFO",
            token=selected["token"],
            quantity=instrument.quantity,
            order_type=instrument.order_type,
            product_type=instrument.product_type,
        )

    # ---------------------------------------------------------
    # MCX Resolution
    # ---------------------------------------------------------

    def _resolve_mcx(
        self,
        instrument: TradingInstrument,
    ) -> TradingInstrument:
        """
        Resolve the nearest MCX futures contract.
        """

        contracts = self._parser.get_mcx_futures(
            instrument.symbol
        )

        if not contracts:

            raise RuntimeError(
                f"No MCX futures contract found for {instrument.symbol}"
            )

        contracts.sort(

            key=lambda x: datetime.strptime(

                x["expiry"],

                "%d%b%Y",

            )

        )

        selected = contracts[0]

        return TradingInstrument(

            symbol=selected["display_symbol"],

            exchange="MCX",

            token=selected["token"],

            quantity=instrument.quantity,

            order_type=instrument.order_type,

            product_type=instrument.product_type,

        )
