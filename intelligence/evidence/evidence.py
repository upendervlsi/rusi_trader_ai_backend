"""
========================================================================

RUSI Trader AI

Evidence

Represents one analytical opinion generated from a feature.

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.core.feature_id import FeatureId
from intelligence.signals.signal_type import SignalType


@dataclass(frozen=True, slots=True)
class Evidence:
    """
    Evidence produced by an analytical component.

    Attributes
    ----------
    feature_id
        Source feature.

    signal
        BUY / SELL / HOLD.

    confidence
        Confidence score in the range [0.0, 1.0].

    value
        Numeric value used to derive the signal.

    reason
        Human-readable explanation.
    """

    feature_id: FeatureId

    signal: SignalType

    confidence: float

    value: float

    reason: str
