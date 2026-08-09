"""
============================================================
RUSI Trader AI

File    : instrument_manager.py

Purpose :
    Central manager for all tradable instruments.

Responsibilities
----------------
1. Register all instrument loaders.
2. Load instruments once during initialization.
3. Cache instruments in memory.
4. Provide lookup APIs.
5. Hide loader implementation from callers.

Author  : RUSI Trader AI
============================================================
"""

from typing import Dict, List

from market.instrument import Instrument
from market.instrument_registry import InstrumentRegistry
from market.commodity_loader import CommodityLoader


class InstrumentManager:
    """
    Central instrument manager.
    """

    def __init__(self):

        self._registry = InstrumentRegistry()

        self._cache: Dict[str, Instrument] = {}

        self._initialized = False

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(self) -> None:
        """
        Register loaders and build instrument cache.
        """

        if self._initialized:
            return

        # Register available loaders

        self._registry.register(
            "MCX",
            CommodityLoader(),
        )

        # Load instruments

        for market in self._registry.available_markets():

            loader = self._registry.get_loader(market)

            instruments = loader.load()

            self._cache.update(instruments)

        self._initialized = True

    # ---------------------------------------------------------
    # Lookup APIs
    # ---------------------------------------------------------

    def get(self, symbol: str) -> Instrument:
        """
        Return one instrument.
        """

        self._ensure_initialized()

        key = symbol.upper()

        if key not in self._cache:

            raise KeyError(
                f"Instrument '{symbol}' not found."
            )

        return self._cache[key]

    def exists(self, symbol: str) -> bool:

        self._ensure_initialized()

        return symbol.upper() in self._cache

    def all(self) -> Dict[str, Instrument]:

        self._ensure_initialized()

        return dict(self._cache)

    def by_exchange(
        self,
        exchange: str,
    ) -> List[Instrument]:

        self._ensure_initialized()

        exchange = exchange.upper()

        return [

            instrument

            for instrument in self._cache.values()

            if instrument.exchange.upper() == exchange

        ]

    def by_type(
        self,
        instrument_type: str,
    ) -> List[Instrument]:

        self._ensure_initialized()

        instrument_type = instrument_type.upper()

        return [

            instrument

            for instrument in self._cache.values()

            if instrument.instrument_type.upper()
            == instrument_type

        ]

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _ensure_initialized(self):

        if not self._initialized:

            self.initialize()
