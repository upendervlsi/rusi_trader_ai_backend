"""
RUSI Trader AI

Dynamic Stock Options Universe

Stage 3

Builds the complete NSE stock-options universe directly from
the normalized instrument master.

This module is intentionally independent of the existing
NIFTY option-resolution/runtime path.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class StockOptionsUniverse:
    """
    Dynamic universe of NSE stock-option contracts.

    Source:
        InstrumentMasterParser.records

    Selection:
        exchange == NFO
        segment == OPTSTK

    No stock symbols are hardcoded.
    """

    def __init__(self, parser):
        self.parser = parser
        self._stocks: dict[str, dict[str, Any]] = {}

    # ---------------------------------------------------------
    # Build
    # ---------------------------------------------------------

    def build(self) -> dict[str, dict[str, Any]]:
        """
        Build the complete stock-options universe.
        """

        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for record in self.parser.records:

            if str(record.get("exchange", "")).upper() != "NFO":
                continue

            if str(record.get("segment", "")).upper() != "OPTSTK":
                continue

            symbol = str(record.get("symbol", "")).strip().upper()

            if not symbol:
                continue

            grouped[symbol].append(record)

        stocks: dict[str, dict[str, Any]] = {}

        for symbol, raw_contracts in sorted(grouped.items()):

            contracts = []

            for raw_contract in raw_contracts:
                contract = dict(raw_contract)

                display_symbol = str(
                    contract.get("display_symbol", "")
                ).upper().strip()

                if display_symbol.endswith("CE"):
                    contract["option_type"] = "CE"

                elif display_symbol.endswith("PE"):
                    contract["option_type"] = "PE"

                if contract.get("strike") not in (None, ""):
                    contract["strike"] = self._normalize_strike(
                        contract.get("strike")
                    )

                contracts.append(contract)

            ce_contracts = [
                c
                for c in contracts
                if c.get("option_type") == "CE"
            ]

            pe_contracts = [
                c
                for c in contracts
                if c.get("option_type") == "PE"
            ]

            expiries = sorted(
                {
                    str(c.get("expiry", "")).strip()
                    for c in contracts
                    if c.get("expiry")
                }
            )

            strikes = sorted(
                {
                    self._normalize_strike(c.get("strike"))
                    for c in contracts
                    if c.get("strike") not in (None, "")
                }
            )

            lot_sizes = sorted(
                {
                    int(float(c.get("lotsize", 0)))
                    for c in contracts
                    if c.get("lotsize") not in (None, "")
                    and float(c.get("lotsize", 0)) > 0
                }
            )

            stocks[symbol] = {
                "symbol": symbol,
                "exchange": "NFO",
                "contract_count": len(contracts),
                "ce_count": len(ce_contracts),
                "pe_count": len(pe_contracts),
                "expiries": expiries,
                "strike_count": len(strikes),
                "strike_min": min(strikes) if strikes else None,
                "strike_max": max(strikes) if strikes else None,
                "lot_sizes": lot_sizes,
                "tokens": [
                    str(c.get("token", ""))
                    for c in contracts
                    if c.get("token") not in (None, "")
                ],
                "contracts": contracts,
            }

        self._stocks = stocks
        return stocks

    # ---------------------------------------------------------
    # Accessors
    # ---------------------------------------------------------

    @property
    def stocks(self) -> dict[str, dict[str, Any]]:
        return self._stocks

    @property
    def stock_symbols(self) -> list[str]:
        return sorted(self._stocks.keys())

    @property
    def stock_count(self) -> int:
        return len(self._stocks)

    @property
    def contract_count(self) -> int:
        return sum(
            stock["contract_count"]
            for stock in self._stocks.values()
        )

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def get_stock(self, symbol: str):
        return self._stocks.get(
            str(symbol).strip().upper()
        )

    def get_contracts(self, symbol: str) -> list[dict[str, Any]]:
        stock = self.get_stock(symbol)

        if not stock:
            return []

        return stock["contracts"]

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        return {
            "stock_count": self.stock_count,
            "contract_count": self.contract_count,
            "stocks": self.stock_symbols,
        }

    def print_summary(self) -> None:

        print()
        print("=" * 70)
        print("Dynamic Stock Options Universe")
        print("=" * 70)
        print(f"Stock Underlyings : {self.stock_count}")
        print(f"OPTSTK Contracts  : {self.contract_count}")
        print("=" * 70)

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_strike(value) -> float:
        """
        Angel instrument-master strikes may be stored ×100.
        Keep normalization consistent with the existing
        instrument-master logic.
        """

        strike = float(value)

        strike /= 100.0

        return strike
