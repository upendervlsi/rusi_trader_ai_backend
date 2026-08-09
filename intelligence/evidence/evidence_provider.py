"""
========================================================================

RUSI Trader AI

Evidence Provider

Base interface for all evidence providers.

========================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.models.feature_store import FeatureStore


class EvidenceProvider(ABC):
    """
    Base class for all evidence providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Provider name.
        """
        ...

    @abstractmethod
    def generate(
        self,
        feature_store: FeatureStore,
        context: EvidenceContext,
    ) -> None:
        """
        Generate evidence and add it into the context.
        """
        ...
