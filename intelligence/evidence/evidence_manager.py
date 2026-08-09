"""
========================================================================

RUSI Trader AI

Evidence Manager

Executes all registered evidence providers.

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.evidence.evidence_provider_registry import (
    EvidenceProviderRegistry,
)
from intelligence.models.feature_store import FeatureStore


class EvidenceManager:
    """
    Executes every registered evidence provider.
    """

    def __init__(
        self,
        registry: EvidenceProviderRegistry,
    ) -> None:

        self._registry = registry

    # ---------------------------------------------------------

    def generate(
        self,
        feature_store: FeatureStore,
    ) -> EvidenceContext:
        """
        Generate evidence from all registered providers.
        """

        context = EvidenceContext()

        for provider in self._registry.providers:

            provider.generate(
                feature_store,
                context,
            )

        return context

    # ---------------------------------------------------------

    @property
    def provider_count(
        self,
    ) -> int:

        return self._registry.count()
