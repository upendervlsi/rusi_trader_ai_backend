"""
========================================================================

RUSI Trader AI

Rule Result

========================================================================
"""

from dataclasses import dataclass

from intelligence.signals.signal_type import SignalType


@dataclass(frozen=True)
class RuleResult:
    """
    Result returned by a rule evaluation.
    """

    signal: SignalType

    confidence: float

    reason: str
