"""
============================================================

Base Intelligence Engine

============================================================
"""

from abc import ABC
from abc import abstractmethod

from common.engine_result import EngineResult
from market_data.market_snapshot import MarketSnapshot


class BaseEngine(ABC):
    """
    Base interface for every intelligence engine.

    All engines must:
      1. Validate the input snapshot.
      2. Analyze the market.
      3. Return a standardized EngineResult.
    """
    @property
    def name(self):

        return self.__class__.__name__
    @abstractmethod
    def verify(self, snapshot: MarketSnapshot) -> bool:
        """
        Validate that sufficient market data is available.
        """
        pass

    @abstractmethod
    def analyze(self, snapshot: MarketSnapshot) -> EngineResult:
        """
        Analyze the market snapshot and return EngineResult.
        """
        pass
