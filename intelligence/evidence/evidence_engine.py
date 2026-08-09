"""
========================================================================

RUSI Trader AI

Evidence Engine

Description
-----------
High-level orchestration layer for evidence generation.

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.evidence import Evidence
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.evidence.evidence_manager import EvidenceManager


class EvidenceEngine:
    """
    High-level evidence generation engine.
    """

    def __init__(
        self,
        manager: EvidenceManager,
    ) -> None:

        self._manager = manager

    @property
    def manager(self) -> EvidenceManager:

        return self._manager

    def calculate(
        self,
        context: EvidenceContext,
    ) -> list[Evidence]:

        return self._manager.generate(
            context
        )

    def provider_count(
        self,
    ) -> int:

        return self._manager.count()
