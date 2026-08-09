"""
=============================================================
RUSI Trader AI

Instrument Master Parser

Converts Angel Instrument Master into an internal searchable
database.

Sprint-18
=============================================================
"""

from __future__ import annotations

import json

from pathlib import Path
from typing import Any


class InstrumentMasterParser:
    """
    Parses Angel Instrument Master.

    The downloaded broker schema is preserved exactly as
    received.

    Internally we normalize every record so the remaining
    application never depends on broker specific field names.
    """

    def __init__(self):

        self._records: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # Loading
    # ---------------------------------------------------------

    def load(
        self,
        source,
    ) -> None:

        """
        Accept either

            Path
            list[dict]
        """

        if isinstance(source, Path):

            with source.open(
                "r",
                encoding="utf-8",
            ) as fp:

                data = json.load(fp)

        else:

            data = source

        self._records.clear()

        for item in data:

            self._records.append(
                self._normalize(item)
            )

    # ---------------------------------------------------------
    # Normalize
    # ---------------------------------------------------------

    def _normalize(
        self,
        record: dict,
    ) -> dict:

        return {

            # -------------------------------------------------
            # Internal Names
            # -------------------------------------------------

            "symbol":
                record.get("name", ""),

            "display_symbol":
                record.get("symbol", ""),

            "exchange":
                record.get("exch_seg", ""),

            "segment":
                record.get(
                    "instrumenttype",
                    "",
                ),

            "token":
                str(
                    record.get(
                        "token",
                        "",
                    )
                ),

            "expiry":
                record.get(
                    "expiry",
                    "",
                ),

            "strike":
                record.get(
                    "strike",
                    "",
                ),

            "lotsize":
                record.get(
                    "lotsize",
                    "",
                ),

            # -------------------------------------------------
            # Original Broker Record
            # -------------------------------------------------

            "raw":
                record,

        }

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def records(self):

        return self._records

    def count(self):

        return len(
            self._records
        )

    # ---------------------------------------------------------
    # Generic Queries
    # ---------------------------------------------------------

    def exists(
        self,
        symbol: str,
    ) -> bool:

        return any(

            r["symbol"] == symbol

            for r in self._records

        )

    def get_by_symbol(
        self,
        symbol: str,
    ):

        symbol = symbol.upper()

        return [

            r

            for r in self._records

            if r["symbol"].upper() == symbol

        ]

    def get_by_exchange(
        self,
        exchange: str,
    ):

        exchange = exchange.upper()

        return [

            r

            for r in self._records

            if r["exchange"].upper() == exchange

        ]

    def get_by_token(
        self,
        token: str,
    ):

        token = str(token)

        for record in self._records:

            if record["token"] == token:

                return record

        return None

    def get_by_exchange_symbol(
        self,
        exchange: str,
        symbol: str,
    ):

        exchange = exchange.upper()

        symbol = symbol.upper()

        return [

            r

            for r in self._records

            if (

                r["exchange"].upper() == exchange

                and

                r["symbol"].upper() == symbol

            )

        ]

    # ---------------------------------------------------------
    # Debug
    # ---------------------------------------------------------

    def summary(self):

        print()

        print("=" * 60)
        print("Instrument Master Summary")
        print("=" * 60)

        print(
            "Records :",
            self.count(),
        )

        exchanges = {

            r["exchange"]

            for r in self._records

        }

        print(
            "Exchanges :",
            sorted(exchanges),
        )

        print("=" * 60)

    # ---------------------------------------------------------
    # NFO Queries
    # ---------------------------------------------------------

    def get_nfo_futures(
        self,
        symbol: str,
    ):

        symbol = symbol.upper()

        return [

            r

            for r in self._records

            if (

                r["exchange"].upper() == "NFO"

                and

                r["symbol"].upper() == symbol

                and

                r["segment"].upper() in (

                    "FUTIDX",

                    "FUTSTK",

                )

            )

        ]

    def get_nfo_options(
        self,
        symbol: str,
    ):

        symbol = symbol.upper()

        return [

            r

            for r in self._records

            if (

                r["exchange"].upper() == "NFO"

                and

                r["symbol"].upper() == symbol

                and

                r["segment"].upper() in (

                    "OPTIDX",

                    "OPTSTK",

                )

            )

        ]

    # ---------------------------------------------------------
    # MCX Queries
    # ---------------------------------------------------------

    def get_mcx_futures(
        self,
        symbol: str,
    ):
        """
        Return all MCX Futures contracts
        for the requested commodity.

        NOTE:
        No sorting is performed here.
        Contract selection is handled by
        InstrumentResolver.
        """

        symbol = symbol.upper()

        return [

            r

            for r in self._records

            if (

                r["exchange"].upper() == "MCX"

                and

                r["symbol"].upper() == symbol

                and

                r["segment"].upper() == "FUTCOM"

            )

        ]

    def get_mcx_options(
        self,
        symbol: str,
    ):
        """
        Return all MCX Option contracts for the
        requested commodity.
        """

        symbol = symbol.upper()

        return [

            r

            for r in self._records

            if (

                r["exchange"].upper() == "MCX"

                and

                r["symbol"].upper() == symbol

                and

                r["segment"].upper() == "OPTFUT"

            )

        ]
