"""
========================================================================

RUSI Trader AI

Signal Result

========================================================================
"""

from dataclasses import dataclass

from intelligence.core.feature_id import FeatureId
from intelligence.signals.signal_type import SignalType


@dataclass(frozen=True)
class SignalResult:
    """
    Standard result produced by a signal generator.
    """

    feature_id: FeatureId

    signal: SignalType

    confidence: float

    reason: str
