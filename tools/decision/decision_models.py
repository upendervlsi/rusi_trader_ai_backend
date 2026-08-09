"""
============================================================
RUSI Trader AI

Decision Models

Common AI decision data structures.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import UTC, datetime


class TradeSignal(Enum):
    """
    Trading decision.
    """

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalStrength(Enum):
    """
    Signal strength classification.
    """

    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MEDIUM = "MEDIUM"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


@dataclass(slots=True)
class IndicatorSnapshot:
    """
    Snapshot of all indicator values.
    """

    values: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class DecisionResult:
    """
    Final AI decision.
    """

    symbol: str

    signal: TradeSignal

    confidence: float

    strength: SignalStrength

    indicators: IndicatorSnapshot

    reasons: list[str] = field(default_factory=list)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    metadata: dict[str, object] = field(
        default_factory=dict
    )

    def add_reason(
        self,
        reason: str,
    ) -> None:

        self.reasons.append(reason)

    def add_metadata(
        self,
        key: str,
        value: object,
    ) -> None:

        self.metadata[key] = value
