"""
========================================================================

Base Evidence Provider

========================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import EvidenceContext


class BaseEvidenceProvider(ABC):

    @abstractmethod
    def evaluate(
        self,
        context: EvidenceContext,
    ) -> Evidence:
        """
        Produce one Evidence object from the supplied context.
        """
        raise NotImplementedError
