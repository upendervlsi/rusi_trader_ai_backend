"""
============================================================

Base Data Source Interface

============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseDataSource(ABC):
    """
    Contract implemented by every broker/provider.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish connection."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Return connection status."""
        raise NotImplementedError

    @abstractmethod
    def get_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ) -> Any:
        """
        Returns the provider's raw historical candle response.

        NOTE:
        The response is intentionally provider-specific.
        Conversion into our domain model is handled by
        MarketSnapshotBuilder.
        """
        raise NotImplementedError
