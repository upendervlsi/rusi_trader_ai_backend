"""
============================================================

Market Snapshot Builder

============================================================
"""

from market_data.market_snapshot import MarketSnapshot
from indicators.indicator_manager import IndicatorManager
from intelligence.market_structure.market_structure_engine import (
    MarketStructureEngine,
)

class MarketSnapshotBuilder:

    def __init__(self):

        self._indicator_manager = IndicatorManager()
        self._structure = MarketStructureEngine()
    def build(self, candles):

        if not candles:
            raise ValueError("No candle data available.")

        snapshot = MarketSnapshot(
            candles=candles,
            latest_candle=candles[-1],
        )

        self._indicator_manager.populate_snapshot(snapshot)
        snapshot.analysis.market_structure = (
            self._structure.analyze(snapshot)
        )
        return snapshot
