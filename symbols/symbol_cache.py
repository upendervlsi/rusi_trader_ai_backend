"""
============================================================

Symbol Cache

============================================================
"""

from __future__ import annotations

from symbols.symbol import TradingSymbol


class SymbolCache:

    def __init__(self):

        self._cache: dict[str, TradingSymbol] = {}

    def put(self, symbol: TradingSymbol):

        self._cache[symbol.symbol.upper()] = symbol

    def get(self, symbol: str):

        return self._cache.get(symbol.upper())

    def clear(self):

        self._cache.clear()

    def size(self):

        return len(self._cache)
