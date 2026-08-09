"""
============================================================

Market Scanner Result

============================================================
"""

from dataclasses import dataclass


@dataclass
class ScannerResult:

    symbol: str = ""

    exchange: str = ""

    signal: str = ""

    confidence: float = 0.0

    score: float = 0.0

    entry: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    option_symbol: str = ""

    underlying: str = ""
