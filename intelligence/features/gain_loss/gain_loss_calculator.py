"""
========================================================================

RUSI Trader AI

Gain Loss Calculator

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class GainLossSeries:
    """
    Holds separated gain and loss series.
    """

    gains: List[float]
    losses: List[float]


class GainLossCalculator:
    """
    Separates price changes into gains and losses.
    """

    def calculate(
        self,
        price_changes: List[float],
    ) -> GainLossSeries:

        gains: List[float] = []
        losses: List[float] = []

        for change in price_changes:

            if change >= 0:

                gains.append(change)
                losses.append(0.0)

            else:

                gains.append(0.0)
                losses.append(abs(change))

        return GainLossSeries(
            gains=gains,
            losses=losses,
        )
