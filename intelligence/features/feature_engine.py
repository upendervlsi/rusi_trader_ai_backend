"""
========================================================================

RUSI Trader AI

Feature Engine

Description
-----------
High-level orchestration layer for feature calculation.

The FeatureEngine owns the FeatureManager and provides a simple API
for generating a FeatureStore from a MarketSeries.

========================================================================
"""

from __future__ import annotations

from intelligence.features.feature_manager import FeatureManager
from intelligence.features.feature_registry import FeatureRegistry
from intelligence.models.feature_store import FeatureStore
from intelligence.models.market_series import MarketSeries


class FeatureEngine:
    """
    High-level feature calculation engine.
    """

    def __init__(
        self,
        registry: FeatureRegistry,
    ) -> None:

        self._manager = FeatureManager(registry)

    @property
    def manager(self) -> FeatureManager:
        """
        Returns the underlying FeatureManager.
        """

        return self._manager

    def calculate(
        self,
        series: MarketSeries,
    ) -> FeatureStore:
        """
        Calculate every registered feature and return
        the populated FeatureStore.
        """

        feature_store = FeatureStore()

        self._manager.calculate_all(
            series=series,
            feature_store=feature_store,
        )

        return feature_store

    def calculate_into(
        self,
        series: MarketSeries,
        feature_store: FeatureStore,
    ) -> FeatureStore:
        """
        Populate an existing FeatureStore.
        """

        self._manager.calculate_all(
            series=series,
            feature_store=feature_store,
        )

        return feature_store

    def registered_features(self):
        """
        Return all registered feature identifiers.
        """

        return self._manager.registered_features()

    def feature_count(self) -> int:
        """
        Number of registered feature calculators.
        """

        return self._manager.count()
