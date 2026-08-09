"""
============================================================
RUSI Trader AI

V1.0

Pipeline Configuration
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PipelineConfig:
    """
    Configuration for the end-to-end trading pipeline.
    """

    paper_trading: bool = True

    exchange: str = "NSE"

    timeframe: str = "5m"

    scanner_enabled: bool = True

    indicator_enabled: bool = True

    decision_enabled: bool = True

    confidence_enabled: bool = True

    risk_enabled: bool = True

    portfolio_enabled: bool = True

    execution_enabled: bool = True

    def validate(self) -> None:

        if not self.exchange:
            raise ValueError("Exchange cannot be empty.")

        if not self.timeframe:
            raise ValueError("Timeframe cannot be empty.")

    def __str__(self):

        mode = "PAPER" if self.paper_trading else "LIVE"

        return (
            f"PipelineConfig("
            f"mode={mode}, "
            f"exchange={self.exchange}, "
            f"timeframe={self.timeframe})"
        )

    __repr__ = __str__
