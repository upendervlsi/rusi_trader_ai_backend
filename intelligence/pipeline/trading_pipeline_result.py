"""
========================================================================

RUSI Trader AI

Trading Pipeline Result

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.decision.decision_result import DecisionResult
from intelligence.market.market_regime import MarketRegime
from intelligence.risk.risk_result import RiskResult
from intelligence.trading.trade_plan import TradePlan


@dataclass(frozen=True)
class TradingPipelineResult:

    regime: MarketRegime

    decision: DecisionResult

    trade_plan: TradePlan

    risk_result: RiskResult
