"""
============================================================
RUSI Trader AI

V1.0

Pipeline Models
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class TradingRequest:
    """
    Input request for the end-to-end trading pipeline.
    """

    symbol: str
    exchange: str = "NSE"
    timeframe: str = "5m"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TradingContext:
    """
    Shared runtime context across all pipeline stages.
    """

    request: TradingRequest

    scanner_result: Any = None
    indicator_result: Any = None
    decision_result: Any = None
    confidence_result: Any = None
    risk_result: Any = None
    portfolio_result: Any = None
    execution_result: Any = None

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineResult:
    """
    Final pipeline execution result.
    """

    success: bool
    context: TradingContext
    message: str = ""

    from datetime import UTC, datetime

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    def __str__(self) -> str:
        return (
            f"PipelineResult("
            f"success={self.success}, "
            f"symbol={self.context.request.symbol})"
        )

    __repr__ = __str__
