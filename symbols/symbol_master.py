"""
============================================================

Symbol Master

============================================================
"""

from __future__ import annotations

from symbols.symbol_cache import SymbolCache


class SymbolMaster:

    def __init__(self):

        self._cache = SymbolCache()

    @property
    def cache(self):

        return self._cache
