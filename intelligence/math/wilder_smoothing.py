"""
========================================================================

RUSI Trader AI

Wilder Smoothing Calculator

========================================================================
"""

from __future__ import annotations

from typing import List


class WilderSmoothingCalculator:
    """
    Implements Wilder's smoothing algorithm.

    Used by:

    - ATR
    - RSI
    - ADX

    Any indicator requiring Wilder's moving average.
    """

    def calculate(
        self,
        values: List[float],
        period: int,
    ) -> List[float]:
        """
        Returns the complete Wilder smoothed series.
        """

        if period <= 0:
            raise ValueError("Period must be greater than zero.")

        if len(values) < period:
            raise ValueError(
                "Not enough values for Wilder smoothing."
            )

        smoothed: List[float] = []

        # First value = Simple Moving Average
        first = sum(values[:period]) / period

        smoothed.append(first)

        previous = first

        # Wilder smoothing
        for value in values[period:]:

            current = (
                (
                    previous * (period - 1)
                )
                + value
            ) / period

            smoothed.append(current)

            previous = current

        return smoothed
