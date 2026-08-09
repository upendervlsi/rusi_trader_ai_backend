"""
============================================================

RUSI Trader AI

Base Analyzer

Every analyzer inherits from this class.

============================================================
"""

from abc import ABC
from abc import abstractmethod

from .analyzer_result import AnalyzerResult


class BaseAnalyzer(ABC):

    """
    Base class for all intelligence analyzers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Analyzer name.
        """
        pass

    @abstractmethod
    def analyze(
        self,
        *args,
        **kwargs,
    ) -> AnalyzerResult:
        """
        Analyze input data and return AnalyzerResult.
        """
        pass
