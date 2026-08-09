"""
============================================================

Evidence Bundle

============================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class EvidenceBundle:
    """
    Evidence generated from all trading features.
    """

    bullish_score: float = 0.0

    bearish_score: float = 0.0

    neutral_score: float = 0.0

    confidence_score: float = 0.0

    bullish_reasons: list[str] | None = None

    bearish_reasons: list[str] | None = None

    neutral_reasons: list[str] | None = None

    def __post_init__(self):

        if self.bullish_reasons is None:
            self.bullish_reasons = []

        if self.bearish_reasons is None:
            self.bearish_reasons = []

        if self.neutral_reasons is None:
            self.neutral_reasons = []
