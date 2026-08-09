"""
========================================================================

RUSI Trader AI

Evidence Context

Stores all generated evidences for the current market snapshot.

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from intelligence.evidence.evidence import Evidence
from intelligence.signals.signal_type import SignalType


@dataclass(slots=True)
class EvidenceContext:
    """
    Central repository for all generated evidence.
    """

    evidences: list[Evidence] = field(default_factory=list)

    def add(
        self,
        evidence: Evidence,
    ) -> None:
        """
        Add one evidence.
        """

        self.evidences.append(
            evidence
        )

    @property
    def count(
        self,
    ) -> int:
        """
        Total evidence count.
        """

        return len(
            self.evidences
        )

    def bullish(
        self,
    ) -> list[Evidence]:
        """
        Return BUY evidences.
        """

        return [
            evidence
            for evidence in self.evidences
            if evidence.signal == SignalType.BUY
        ]

    def bearish(
        self,
    ) -> list[Evidence]:
        """
        Return SELL evidences.
        """

        return [
            evidence
            for evidence in self.evidences
            if evidence.signal == SignalType.SELL
        ]

    def neutral(
        self,
    ) -> list[Evidence]:
        """
        Return HOLD evidences.
        """

        return [
            evidence
            for evidence in self.evidences
            if evidence.signal == SignalType.HOLD
        ]

    def clear(
        self,
    ) -> None:
        """
        Remove all evidence.
        """

        self.evidences.clear()
