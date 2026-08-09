"""
============================================================

RUSI Trader AI

Base Indicator

All technical indicators inherit from this class.

============================================================
"""

from abc import ABC
from abc import abstractmethod


class BaseIndicator(ABC):

    @abstractmethod
    def calculate(self, candles):
        """
        Calculate indicator values.

        Parameters
        ----------
        candles : list[Candle]

        Returns
        -------
        object
        """
        pass
