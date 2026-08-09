"""
========================================================================

RUSI Trader AI

Trading Pipeline

========================================================================
"""

from __future__ import annotations

from intelligence.decision.decision_engine import DecisionEngine
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.evidence.evidence_manager import EvidenceManager
from intelligence.market.market_regime_classifier import (
    MarketRegimeClassifier,
)
from intelligence.pipeline.trading_pipeline_result import (
    TradingPipelineResult,
)
from intelligence.risk.risk_manager import RiskManager
from intelligence.trading.trade_planner import TradePlanner


class TradingPipeline:

    def __init__(self):

        self._evidence_manager = EvidenceManager()

        self._regime_classifier = MarketRegimeClassifier()

        self._decision_engine = DecisionEngine()

        self._trade_planner = TradePlanner()

        self._risk_manager = RiskManager()

    def run(
        self,
        context: EvidenceContext,
        capital: float,
    ) -> TradingPipelineResult:

        evidences = self._evidence_manager.generate(
            context
        )

        regime = self._regime_classifier.classify(
            context
        )

        decision = self._decision_engine.decide(
            evidences
        )
        trade_plan = self._trade_planner.create_plan(
            decision,
            context,
        )

        risk = self._risk_manager.evaluate(
            trade_plan,
            capital,
        )

        return TradingPipelineResult(
            regime=regime,
            decision=decision,
            trade_plan=trade_plan,
            risk_result=risk,
        )
