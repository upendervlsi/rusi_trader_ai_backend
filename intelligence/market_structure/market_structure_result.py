"""
============================================================

Market Structure Result

============================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class MarketStructureResult:

    higher_high: bool = False
    higher_low: bool = False

    lower_high: bool = False
    lower_low: bool = False

    bullish_structure: bool = False
    bearish_structure: bool = False

    confidence: float = 0.0

    reasons: list[str] | None = None
