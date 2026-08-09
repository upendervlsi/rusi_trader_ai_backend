"""
============================================================
RUSI Trader AI

File    : instrument_registry.py

Purpose :
    Registry for instrument loaders.

Author  : RUSI Trader AI
============================================================
"""

from typing import Dict, Protocol

from market.instrument import Instrument


class InstrumentLoader(Protocol):
    """
    Interface implemented by all instrument loaders.
    """

    def load(self) -> Dict[str, Instrument]:
        ...


class InstrumentRegistry:
    """
    Registry that manages all instrument loaders.
    """

    def __init__(self):

        self._loaders: Dict[str, InstrumentLoader] = {}

    def register(
        self,
        market: str,
        loader: InstrumentLoader,
    ) -> None:
        """
        Register a loader.
        """

        key = market.upper()

        if key in self._loaders:
            raise ValueError(
                f"Loader already registered: {market}"
            )

        self._loaders[key] = loader

    def unregister(self, market: str) -> None:
        """
        Remove a loader.
        """

        self._loaders.pop(market.upper(), None)

    def get_loader(
        self,
        market: str,
    ) -> InstrumentLoader:
        """
        Return loader for market.
        """

        key = market.upper()

        if key not in self._loaders:
            raise KeyError(
                f"No loader registered for '{market}'"
            )

        return self._loaders[key]

    def available_markets(self):
        """
        Return registered markets.
        """

        return sorted(self._loaders.keys())
