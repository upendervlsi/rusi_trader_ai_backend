"""
============================================================

Historical Loader

============================================================
"""

from __future__ import annotations

from datetime import datetime

from datasource.base_datasource import BaseDataSource


class HistoricalLoader:
    """
    Broker-independent historical data loader.
    """

    def __init__(self, datasource: BaseDataSource):
        self._datasource = datasource

    def load(
        self,
        symbol: str,
        timeframe: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ):
        if not self._datasource.is_connected():
            raise RuntimeError("Datasource is not connected.")

        return self._datasource.get_historical_candles(
            symbol=symbol,
            timeframe=timeframe,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
        )
