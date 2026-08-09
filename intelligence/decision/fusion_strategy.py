"""
========================================================================

RUSI Trader AI

Fusion Strategy

========================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.decision.evidence_fusion import FusionResult
from intelligence.evidence.evidence import Evidence


class FusionStrategy(ABC):
    """
    Base interface for all evidence fusion strategies.
    """

    @abstractmethod
    def fuse(
        self,
        evidences: list[Evidence],
    ) -> FusionResult:
        raise NotImplementedError
