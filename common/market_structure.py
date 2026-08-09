"""
============================================================

Market Structure

============================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class MarketStructure:

    higher_high: bool = False

    higher_low: bool = False

    lower_high: bool = False

    lower_low: bool = False

    trend: str = "UNKNOWN"
