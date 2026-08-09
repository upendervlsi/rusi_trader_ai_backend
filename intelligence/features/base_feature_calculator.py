"""
========================================================================

Base Feature Calculator

========================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.features.feature_definition import FeatureDefinition
from intelligence.models.feature_store import FeatureStore
from intelligence.models.market_series import MarketSeries


class BaseFeatureCalculator(ABC):
    """
    Base class for every feature calculator.
    """

    @property
    @abstractmethod
    def definition(self) -> FeatureDefinition:
        """
        Returns calculator metadata.
        """
        ...

    @abstractmethod
    def calculate(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> None:
        """
        Calculates one or more features from the supplied MarketSeries
        and stores the results in the FeatureStore.
        """
        ...
