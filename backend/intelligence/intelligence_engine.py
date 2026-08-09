"""
============================================================

RUSI Trader AI

Intelligence Engine

============================================================
"""

from dataclasses import dataclass

from backend.models.market_snapshot import MarketSnapshot

from .analyzer_registry import AnalyzerRegistry

from .confidence_engine import ConfidenceEngine
from .recommendation_engine import RecommendationEngine


@dataclass
class IntelligenceResult:

    recommendation: str

    confidence: float

    score: float

    risk: str

    auto_trade: bool

    reasons: list[str]

    analyzers: list


class IntelligenceEngine:

    def __init__(self):

        self.analyzers = (

            AnalyzerRegistry.get_analyzers()

        )

        self.confidence = (

            ConfidenceEngine()

        )

        self.recommendation = (

            RecommendationEngine()

        )

    #------------------------------------------------------
    # Evaluate
    #------------------------------------------------------

    def evaluate(

        self,

        snapshot: MarketSnapshot,

    ) -> IntelligenceResult:

        analyzer_results = []

        for analyzer in self.analyzers:

            analyzer_results.append(

                analyzer.analyze(

                    snapshot,

                )

            )

        confidence = (

            self.confidence.calculate(

                analyzer_results,

            )

        )

        recommendation = (

            self.recommendation.generate(

                confidence,

            )

        )

        return IntelligenceResult(

            recommendation=

                recommendation.recommendation,

            confidence=

                recommendation.confidence,

            score=

                recommendation.score,

            risk=

                recommendation.risk,

            auto_trade=

                recommendation.auto_trade,

            reasons=

                recommendation.reasons,

            analyzers=

                analyzer_results,

        )
