"""
========================================================================

RUSI Trader AI

Base Signal Generator

========================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.models.feature_store import FeatureStore
from intelligence.signals.signal_result import SignalResult


class BaseSignalGenerator(ABC):
    """
    Base class for all signal generators.
    """

    def generate(
        self,
        feature_store: FeatureStore,
    ) -> SignalResult:
        """
        Template method.
        """

        return self._generate(
            feature_store
        )

    @abstractmethod
    def _generate(
        self,
        feature_store: FeatureStore,
    ) -> SignalResult:
        """
        Implemented by concrete generators.
        """
        raise NotImplementedError
