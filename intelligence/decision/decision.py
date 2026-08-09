"""
============================================================

RUSI Trader AI

Decision

============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence.signals.signal_type import SignalType


@dataclass(slots=True)
class Decision:
    """
    Final trading decision.
    """

    signal: SignalType

    confidence: float

    score: float

    reasons: list[str] = field(default_factory=list)
