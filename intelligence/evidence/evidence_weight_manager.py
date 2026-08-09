"""
============================================================

Evidence Weight Manager

============================================================
"""

from __future__ import annotations


class EvidenceWeightManager:

    def __init__(self) -> None:

        self._weights = {
            "EMA": 1.0,
            "MACD": 1.2,
            "RSI": 0.8,
        }

    def weight(
        self,
        indicator: str,
    ) -> float:

        return self._weights.get(
            indicator,
            1.0,
        )
