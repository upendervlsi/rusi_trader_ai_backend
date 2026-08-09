"""
============================================================
RUSI Trader AI

Scanner Models

Defines the common data models exchanged between all
scanner implementations.

These models are intentionally technology independent.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# Scanner Request
# ============================================================

@dataclass(slots=True)
class ScannerRequest:
    """
    Input supplied to any scanner.
    """

    scanner_type: str
    symbol: str | None = None
    exchange: str | None = None
    timeframe: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Scanner Evidence
# ============================================================

@dataclass(slots=True)
class ScannerEvidence:
    """
    Individual evidence produced by a scanner.
    """

    name: str
    value: Any
    weight: float = 1.0
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Scanner Candidate
# ============================================================

@dataclass(slots=True)
class ScannerCandidate:
    """
    One trading candidate discovered by a scanner.
    """

    symbol: str
    exchange: str

    score: float = 0.0
    confidence: float = 0.0

    direction: str | None = None

    evidences: list[ScannerEvidence] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Scanner Result
# ============================================================

@dataclass(slots=True)
class ScannerResult:
    """
    Result returned by a scanner.
    """

    scanner_type: str

    success: bool = True

    candidates: list[ScannerCandidate] = field(default_factory=list)

    messages: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
