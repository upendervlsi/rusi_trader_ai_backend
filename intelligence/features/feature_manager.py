"""
========================================================================

RUSI Trader AI

Feature Manager

Central orchestrator for feature calculation.

========================================================================
"""

from __future__ import annotations

from intelligence.core.feature_id import FeatureId
from intelligence.features.feature_registry import FeatureRegistry
from intelligence.models.feature_store import FeatureStore
from intelligence.models.market_series import MarketSeries


class FeatureManager:
    """
    Executes registered feature calculators.
    """

    def __init__(
        self,
        registry: FeatureRegistry,
    ) -> None:

        self._registry = registry

    def calculate_all(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> None:

        for calculator in self._registry.all():
            calculator.calculate(series, feature_store)

    def calculate(
        self,
        feature: FeatureId,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> None:

        calculator = self._registry.get(feature)

        calculator.calculate(series, feature_store)

    def is_registered(
        self,
        feature: FeatureId,
    ) -> bool:

        return self._registry.exists(feature)

    def registered_features(self):

        return [
            calculator.definition.feature_id
            for calculator in self._registry.all()
        ]

    def count(self) -> int:

        return self._registry.count()
