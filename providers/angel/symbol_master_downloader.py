"""
============================================================

Angel One Symbol Master Downloader

============================================================
"""

from __future__ import annotations

import json
from urllib.request import urlopen

from symbols.symbol import TradingSymbol
from symbols.symbol_master import SymbolMaster


class SymbolMasterDownloader:
    """
    Downloads and loads Angel One symbol master.
    """

    SYMBOL_MASTER_URL = (
        "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    )

    def __init__(self, master: SymbolMaster):
        self._master = master

    def download(self) -> int:

        with urlopen(self.SYMBOL_MASTER_URL, timeout=30) as response:
            records = json.load(response)

        loaded = 0

        for item in records:

            symbol = item.get("symbol")

            if not symbol:
                continue

            trading_symbol = TradingSymbol(
                symbol=symbol.upper(),
                exchange=item.get("exch_seg", ""),
                token=str(item.get("token", "")),
                instrument_type=item.get("instrumenttype", ""),
                name=item.get("name", ""),
                expiry=item.get("expiry") or None,
                strike=float(item["strike"]) if item.get("strike") else None,
                option_type=item.get("optiontype") or None,
            )

            self._master.cache.put(trading_symbol)
            loaded += 1

        return loaded
