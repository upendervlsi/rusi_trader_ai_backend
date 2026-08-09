"""
============================================================

RUSI Trader AI

Market Snapshot Builder

Combines market services into one snapshot.

============================================================
"""

from backend.models.market_snapshot import MarketSnapshot

from backend.services.market_service import MarketService
from backend.services.market_data_service import MarketDataService


class MarketSnapshotBuilder:

    def __init__(self):

        self.market_service = MarketService()

        self.market_data_service = MarketDataService()

    def build(self) -> MarketSnapshot:

        # Refresh latest values
        self.market_data_service.refresh()

        # Return the complete snapshot object
        return self.market_data_service.get_snapshot()
