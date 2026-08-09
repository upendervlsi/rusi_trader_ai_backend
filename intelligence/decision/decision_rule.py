"""
============================================================

Decision Rule

============================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from intelligence.decision.decision import Decision
from intelligence.evidence.evidence_context import EvidenceContext


class DecisionRule(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def evaluate(
        self,
        evidence: EvidenceContext,
    ) -> Decision:
        ...
