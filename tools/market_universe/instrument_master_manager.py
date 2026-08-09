"""
RUSI Trader AI

Instrument Master Manager

Sprint-17 Part-2

Responsibilities

- Manage local instrument master cache
- Refresh instrument master
- Validate cache freshness
- Save/load master JSON
- Provide exchange-aware option lookup

=============================================================
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .constants import (
    MASTER_DIR,
    MASTER_FILE,
    MASTER_TIMESTAMP,
    MASTER_REFRESH_HOURS,
)


class InstrumentMasterManager:

    def __init__(self):

        MASTER_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._option_cache = None

    # -----------------------------------------------------
    # Cache
    # -----------------------------------------------------

    def cache_exists(self) -> bool:

        return MASTER_FILE.exists()

    # -----------------------------------------------------

    def timestamp_exists(self) -> bool:

        return MASTER_TIMESTAMP.exists()

    # -----------------------------------------------------

    def save_master(
        self,
        data: Any,
    ) -> None:

        with MASTER_FILE.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                data,
                fp,
                indent=4,
            )

        # Invalidate in-memory option cache.
        self._option_cache = None

        self._update_timestamp()

    # -----------------------------------------------------

    def load_master(self):

        if not MASTER_FILE.exists():

            raise FileNotFoundError(
                MASTER_FILE
            )

        with MASTER_FILE.open(
            "r",
            encoding="utf-8",
        ) as fp:

            return json.load(fp)

    # -----------------------------------------------------

    def _update_timestamp(self):

        MASTER_TIMESTAMP.write_text(
            datetime.utcnow().isoformat(),
            encoding="utf-8",
        )

    # -----------------------------------------------------

    def cache_age_hours(self):

        if not self.timestamp_exists():

            return None

        value = MASTER_TIMESTAMP.read_text(
            encoding="utf-8",
        ).strip()

        created = datetime.fromisoformat(value)

        delta = datetime.utcnow() - created

        return delta.total_seconds() / 3600.0

    # -----------------------------------------------------

    def refresh_required(self) -> bool:

        if not self.cache_exists():

            return True

        age = self.cache_age_hours()

        if age is None:

            return True

        return age >= MASTER_REFRESH_HOURS

    # -----------------------------------------------------

    def print_status(self):

        print()

        print("=" * 60)

        print("Instrument Master Status")

        print("=" * 60)

        print(
            f"Cache Exists      : "
            f"{self.cache_exists()}"
        )

        print(
            f"Timestamp Exists  : "
            f"{self.timestamp_exists()}"
        )

        print(
            f"Refresh Required  : "
            f"{self.refresh_required()}"
        )

        age = self.cache_age_hours()

        if age is not None:

            print(
                f"Cache Age (Hours) : "
                f"{age:.2f}"
            )

        print("=" * 60)

        print()

    # -----------------------------------------------------
    # Internal Master Cache
    # -----------------------------------------------------

    def _get_option_cache(self):

        if self._option_cache is None:

            self._option_cache = self.load_master()

        return self._option_cache

    # -----------------------------------------------------
    # Normalize Underlying
    # -----------------------------------------------------

    def _normalize_underlying(
        self,
        symbol: str,
    ) -> str:

        symbol = symbol.upper().strip()

        # -------------------------------------------------
        # Standard NSE index underlyings
        # -------------------------------------------------

        if symbol.startswith("BANKNIFTY"):

            return "BANKNIFTY"

        if symbol.startswith("FINNIFTY"):

            return "FINNIFTY"

        if symbol.startswith("MIDCPNIFTY"):

            return "MIDCPNIFTY"

        if symbol.startswith("NIFTY"):

            return "NIFTY"

        # -------------------------------------------------
        # MCX futures
        #
        # Example:
        #
        # CRUDEOIL19AUG26FUT
        # NATURALGAS26AUG26FUT
        #
        # becomes:
        #
        # CRUDEOIL
        # NATURALGAS
        # -------------------------------------------------

        mcx_future = re.match(
            r"^([A-Z0-9]+?)\d{1,2}[A-Z]{3}\d{2}FUT$",
            symbol,
        )

        if mcx_future:

            return mcx_future.group(1)

        # -------------------------------------------------
        # Generic FUT suffix
        # -------------------------------------------------

        if symbol.endswith("FUT"):

            base = symbol[:-3]

            # Remove a trailing MCX-style expiry portion
            # when one is present.
            mcx_expiry = re.match(
                r"^(.+?)\d{1,2}[A-Z]{3}\d{2}$",
                base,
            )

            if mcx_expiry:

                return mcx_expiry.group(1)

            return base

        return symbol

    # -----------------------------------------------------
    # Normalize Strike
    # -----------------------------------------------------

    def _normalize_strike(
        self,
        strike,
    ) -> float:

        strike = float(strike)

        #
        # Angel stores strike ×100
        #

        if strike > 100000:

            strike /= 100.0

        return strike

    # -----------------------------------------------------
    # Option Type
    # -----------------------------------------------------

    def _option_type(
        self,
        symbol: str,
    ) -> str:

        symbol = symbol.upper()

        if symbol.endswith("CE"):

            return "CE"

        if symbol.endswith("PE"):

            return "PE"

        return ""

    # -----------------------------------------------------
    # Build Option Contract Dictionary
    # -----------------------------------------------------

    def _build_option(
        self,
        row,
    ):

        symbol = row.get("symbol")

        if not symbol:

            return None

        strike = row.get("strike")

        if strike is None:

            return None

        lotsize = row.get("lotsize")

        if lotsize is None:

            lotsize = 0

        return {

            "symbol":
                symbol,

            "display_symbol":
                symbol,

            "exchange":
                row.get("exch_seg"),

            "token":
                row.get("token"),

            "strike":
                self._normalize_strike(
                    strike
                ),

            "expiry":
                row.get("expiry"),

            "lotsize":
                int(lotsize),

            "option_type":
                self._option_type(
                    symbol
                ),
        }

    # -----------------------------------------------------
    # Load NFO Options
    # -----------------------------------------------------

    def get_nfo_options(
        self,
        underlying: str,
    ):

        cache = self._get_option_cache()

        underlying = self._normalize_underlying(
            underlying
        )

        options = []

        for row in cache:

            #
            # NFO only
            #

            if row.get("exch_seg") != "NFO":

                continue

            #
            # Index options only
            #

            if row.get("instrumenttype") != "OPTIDX":

                continue

            #
            # Underlying
            #

            if row.get("name") != underlying:

                continue

            option = self._build_option(
                row
            )

            if option is None:

                continue

            options.append(
                option
            )

        return options

    # -----------------------------------------------------
    # Load MCX Options
    # -----------------------------------------------------

    def get_mcx_options(
        self,
        underlying: str,
    ):

        cache = self._get_option_cache()

        underlying = self._normalize_underlying(
            underlying
        )

        options = []

        for row in cache:

            #
            # MCX only
            #

            if row.get("exch_seg") != "MCX":

                continue

            #
            # MCX option contracts
            #
            # Angel's instrument master can represent
            # commodity options using OPTFUT.
            #
            # We also accept OPTCOM / OPTIDX style values
            # defensively without changing NFO behavior.
            #

            instrument_type = (
                row.get("instrumenttype")
                or ""
            ).upper()

            if instrument_type not in (
                "OPTFUT",
                "OPTCOM",
                "OPTIDX",
            ):

                continue

            #
            # Underlying
            #
            #
            # Depending on the Angel master version,
            # the underlying can be represented in
            # either "name" or through the symbol.
            #

            row_name = str(
                row.get("name") or ""
            ).upper()

            row_symbol = str(
                row.get("symbol") or ""
            ).upper()

            normalized_row_name = (
                self._normalize_underlying(
                    row_name
                )
                if row_name
                else ""
            )

            normalized_row_symbol = (
                self._normalize_underlying(
                    row_symbol
                )
                if row_symbol
                else ""
            )

            if underlying not in (
                row_name,
                normalized_row_name,
                normalized_row_symbol,
            ):

                continue

            option = self._build_option(
                row
            )

            if option is None:

                continue

            options.append(
                option
            )

        return options

    # -----------------------------------------------------
    # Exchange-Aware Options
    # -----------------------------------------------------

    def get_options(
        self,
        exchange: str,
        underlying: str,
    ):

        exchange = (
            exchange or ""
        ).upper().strip()

        if exchange == "MCX":

            return self.get_mcx_options(
                underlying
            )

        if exchange == "NFO":

            return self.get_nfo_options(
                underlying
            )

        return []
