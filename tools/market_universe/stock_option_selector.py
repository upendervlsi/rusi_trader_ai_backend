"""
RUSI Trader AI

Stock Option Selector

Stage 6

Purpose
-------
Select stock-option contracts dynamically from the complete
OPTSTK universe.

This module is intentionally separate from the existing
NIFTY option resolver/ranker.

Rules
-----
BULLISH -> CE
BEARISH -> PE
NO_TRADE / HOLD -> no option

Selection is based on:
    1. valid non-expired expiry
    2. directional option type
    3. percentage distance from underlying price

No stock symbols, strikes, expiries, or lot sizes are
hardcoded.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class StockOptionCandidate:
    symbol: str
    option_symbol: str
    exchange: str
    token: str
    strike: float
    expiry: str
    option_type: str
    lot_size: int
    distance_percent: float
    rank: int


class StockOptionSelector:

    def __init__(self, universe):

        self._universe = universe

    # ---------------------------------------------------------
    # Public selection
    # ---------------------------------------------------------

    def select(
        self,
        symbol: str,
        direction: str,
        underlying_price: float,
    ) -> list[StockOptionCandidate]:

        symbol = str(symbol).upper().strip()
        direction = str(direction).upper().strip()
        underlying_price = float(underlying_price)

        if not symbol:
            return []

        if underlying_price <= 0:
            return []

        option_type = self._direction_to_option_type(direction)

        if option_type is None:
            return []

        contracts = self._universe.get_contracts(symbol)

        if not contracts:
            return []

        contracts = [
            contract
            for contract in contracts
            if str(contract.get("option_type", "")).upper()
            == option_type
        ]

        if not contracts:
            return []

        expiry = self._nearest_valid_expiry(contracts)

        if expiry is None:
            return []

        contracts = [
            contract
            for contract in contracts
            if str(contract.get("expiry", "")).strip()
            == expiry
        ]

        candidates = []

        for contract in contracts:

            strike = self._strike(contract)

            if strike is None or strike <= 0:
                continue

            distance_percent = (
                abs(strike - underlying_price)
                / underlying_price
            ) * 100.0

            candidates.append(
                StockOptionCandidate(
                    symbol=symbol,
                    option_symbol=str(
                        contract.get("display_symbol", "")
                    ),
                    exchange=str(
                        contract.get("exchange", "NFO")
                    ),
                    token=str(
                        contract.get("token", "")
                    ),
                    strike=strike,
                    expiry=expiry,
                    option_type=option_type,
                    lot_size=int(
                        float(contract.get("lotsize", 0))
                    ),
                    distance_percent=distance_percent,
                    rank=0,
                )
            )

        candidates.sort(
            key=lambda candidate: (
                candidate.distance_percent,
                candidate.strike,
            )
        )

        ranked = []

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            ranked.append(
                StockOptionCandidate(
                    symbol=candidate.symbol,
                    option_symbol=candidate.option_symbol,
                    exchange=candidate.exchange,
                    token=candidate.token,
                    strike=candidate.strike,
                    expiry=candidate.expiry,
                    option_type=candidate.option_type,
                    lot_size=candidate.lot_size,
                    distance_percent=candidate.distance_percent,
                    rank=index,
                )
            )

        return ranked

    # ---------------------------------------------------------
    # Best candidate
    # ---------------------------------------------------------

    def select_best(
        self,
        symbol: str,
        direction: str,
        underlying_price: float,
    ) -> StockOptionCandidate | None:

        candidates = self.select(
            symbol=symbol,
            direction=direction,
            underlying_price=underlying_price,
        )

        if not candidates:
            return None

        return candidates[0]

    # ---------------------------------------------------------
    # Direction
    # ---------------------------------------------------------

    @staticmethod
    def _direction_to_option_type(
        direction: str,
    ) -> str | None:

        if direction == "BULLISH":
            return "CE"

        if direction == "BEARISH":
            return "PE"

        return None

    # ---------------------------------------------------------
    # Expiry
    # ---------------------------------------------------------

    @staticmethod
    def _nearest_valid_expiry(
        contracts: list[dict],
    ) -> str | None:

        today = datetime.now().date()

        valid = []

        for contract in contracts:

            expiry_text = str(
                contract.get("expiry", "")
            ).strip()

            if not expiry_text:
                continue

            expiry_date = (
                StockOptionSelector._parse_expiry(
                    expiry_text
                )
            )

            if expiry_date is None:
                continue

            if expiry_date >= today:
                valid.append(
                    (expiry_date, expiry_text)
                )

        if not valid:
            return None

        valid.sort(
            key=lambda item: item[0]
        )

        return valid[0][1]

    # ---------------------------------------------------------
    # Expiry parser
    # ---------------------------------------------------------

    @staticmethod
    def _parse_expiry(
        value: str,
    ):

        value = value.strip().upper()

        formats = (
            "%d%b%Y",
            "%d%b%y",
            "%Y-%m-%d",
            "%d-%b-%Y",
            "%d-%b-%y",
        )

        for fmt in formats:

            try:
                return datetime.strptime(
                    value,
                    fmt,
                ).date()

            except ValueError:
                continue

        return None

    # ---------------------------------------------------------
    # Strike
    # ---------------------------------------------------------

    @staticmethod
    def _strike(
        contract: dict,
    ) -> float | None:

        try:
            strike = float(
                contract.get("strike")
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        # StockOptionsUniverse provides the normalized
        # application-level strike value.
        #
        # The raw Angel instrument-master strike remains
        # preserved separately in the contract's "raw" field.

        return strike
