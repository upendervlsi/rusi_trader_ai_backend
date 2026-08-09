"""
========================================================================

RUSI Trader AI

Trading Context

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from intelligence.models.feature_store import FeatureStore
from intelligence.evidence.evidence import Evidence
from trading.pipeline.pipeline_result import PipelineResult


@dataclass(slots=True)
class TradingInstrument:
    """
    Instrument being traded.
    """

    symbol: str

    exchange: str

    token: str

    quantity: int = 1

    order_type: str = "MARKET"

    product_type: str = "INTRADAY"


@dataclass(slots=True)
class TradingContext:
    """
    Runtime context for one trading cycle.
    """

    from intelligence.models.market_snapshot import MarketSnapshot

    market_snapshot: MarketSnapshot

    #
    # Instrument Information
    #
    instrument: TradingInstrument | None = None

    indicators: dict[str, Any] | None = None

    features: FeatureStore | None = None

    evidence: Any = None

    market_regime: Any = None

    decision: Any = None
    #
    # Recommendation generated after Decision Engine
    #
    recommendation: Any = None

    #
    # Execution Policy
    #
    execution_policy: Any = None

    #
    # Order built by Order Builder
    #
    order: Any = None

    #
    # Broker execution result
    #
    broker_result: Any = None

    #
    # Position created after successful execution
    #
    position: Any = None
    trade_plan: Any = None

    risk_result: Any = None

    execution_result: Any = None

    metadata: dict[str, Any] | None = None

    pipeline_results: list[PipelineResult] | None = None

    def __post_init__(self):

        if self.indicators is None:
            self.indicators = {}

        if self.features is None:
            self.features = FeatureStore()

        if self.metadata is None:
            self.metadata = {}

        if self.pipeline_results is None:
            self.pipeline_results = []
