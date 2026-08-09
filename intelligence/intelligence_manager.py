"""
============================================================

Intelligence Manager

============================================================
"""

from intelligence.engine_manager import EngineManager
from intelligence.trend_engine import TrendEngine
from intelligence.market_structure_engine import (
    MarketStructureEngine,
)

class IntelligenceManager:

    def __init__(self):

        self._manager = EngineManager()

        #
        # Register Intelligence Engines
        #


        self._manager.register(
            TrendEngine()
        )

        self._manager.register(
            MarketStructureEngine()
        )
        #
        # Future Engines
        #

        # self._manager.register(RSIEngine())
        # self._manager.register(MACDEngine())
        # self._manager.register(ATREngine())
        # self._manager.register(VolumeEngine())
        # self._manager.register(MarketStructureEngine())
        # self._manager.register(OptionChainEngine())

    def analyze(self, snapshot):

        return self._manager.execute(snapshot)
