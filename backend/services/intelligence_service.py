"""
============================================================

RUSI Trader AI

Intelligence Service

============================================================
"""

from backend.intelligence.intelligence_engine import (
    IntelligenceEngine,
)

from backend.intelligence.decision_engine import (
    DecisionEngine,
)

from backend.services.market_snapshot_builder import (
    MarketSnapshotBuilder,
)


class IntelligenceService:

    def __init__(self):

        self.snapshot_builder = (
            MarketSnapshotBuilder()
        )

        self.intelligence_engine = (
            IntelligenceEngine()
        )

        self.decision_engine = (
            DecisionEngine()
        )

    #------------------------------------------------------
    # Generate Trade Plan
    #------------------------------------------------------

    def generate(self):

        #
        # Latest Market Snapshot
        #

        snapshot = self.snapshot_builder.build()

        #
        # AI Analysis
        #

        intelligence = (

            self.intelligence_engine.evaluate(
                snapshot,
            )

        )

        #
        # Trading Decision
        #

        trade_plan = (

            self.decision_engine.generate(

                snapshot=snapshot,

                recommendation=
                    intelligence.recommendation,

                confidence=
                    intelligence.confidence,

                reasons=
                    intelligence.reasons,

            )

        )

        return trade_plan
