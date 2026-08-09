"""
============================================================
RUSI Trader AI

Market Data Provider

Abstract interface for market data providers.
============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from tools.scanner.scanner_models import ScannerRequest


class MarketDataProvider(ABC):
    """
    Base interface for all market data providers.

    Implementations may retrieve data from:
      - Angel One
      - Zerodha
      - NSE
      - Yahoo Finance
      - CSV
      - Database
      - Historical cache
    """

    @abstractmethod
    def load(
        self,
        request: ScannerRequest,
    ):
        """
        Load market data for a scanner request.

        Returns
        -------
        Market data object (defined later).
        """
        raise NotImplementedError
