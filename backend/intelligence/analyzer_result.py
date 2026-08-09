"""
============================================================

RUSI Trader AI

Analyzer Result

Common result model for all analyzers.

============================================================
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalyzerResult:
    """
    Generic analyzer output.

    Every analyzer (Trend, Momentum, Options,
    Risk, News...) returns this object.
    """

    # Analyzer Name
    name: str

    # Numerical contribution
    score: float

    # Classification
    classification: str

    # Confidence (0-100)
    confidence: float

    # Human readable explanations
    reasons: List[str] = field(
        default_factory=list
    )

    # Optional metadata
    metadata: dict = field(
        default_factory=dict
    )

    @property
    def passed(self) -> bool:
        return self.score >= 0

    def add_reason(
        self,
        reason: str,
    ) -> None:

        self.reasons.append(reason)

    def add_metadata(
        self,
        key: str,
        value,
    ) -> None:

        self.metadata[key] = value
