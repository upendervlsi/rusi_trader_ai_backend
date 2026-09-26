"""
============================================================

RUSI Trader AI

Intelligence Service

Runtime compatibility adapter.

The Trading Engine is the authoritative producer of
market snapshot, intelligence, decision and recommendation.

This service reads the latest completed runtime cycle.

It MUST NOT create a second intelligence calculation.

============================================================
"""

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)

from backend.intelligence.trade_plan import (
    TradePlan,
)


class IntelligenceService:

    def __init__(self):

        self._facade = TradingEngineFacade()

    # ------------------------------------------------------
    # Generate Trade Plan
    # ------------------------------------------------------

    def generate(self):

        #
        # Read the authoritative runtime state.
        #

        state = self._facade.get_runtime_state()

        #
        # Runtime must already contain a completed cycle.
        #

        if state.snapshot is None:

            raise RuntimeError(
                "Trading runtime is not ready. "
                "No completed market snapshot is available."
            )

        #
        # Recommendation is produced by the authoritative
        # trading engine runtime.
        #

        recommendation = state.recommendation

        if recommendation is None:

            raise RuntimeError(
                "Trading runtime is not ready. "
                "No recommendation is available."
            )

        #
        # --------------------------------------------------
        # Legacy TradePlan compatibility adapter
        # --------------------------------------------------
        #
        # The new runtime recommendation is authoritative.
        #
        # Some fields in the old TradePlan do not exist in
        # RecommendationModel. Where possible, obtain them
        # from the runtime decision / execution policy.
        #
        # No trading value is calculated or invented here.
        #

        decision = state.decision
        execution_policy = state.execution_policy

        #
        # Legacy fields
        #

        trade_quality = getattr(
            recommendation,
            "score",
            None,
        )

        target1 = getattr(
            recommendation,
            "target_price",
            None,
        )

        target2 = getattr(
            decision,
            "target2",
            None,
        )

        if target2 is None:

            target2 = getattr(
                decision,
                "target_price2",
                None,
            )

        risk_reward = getattr(
            recommendation,
            "risk_reward",
            None,
        )

        if risk_reward is None:

            risk_reward = ""

        else:

            risk_reward = str(
                risk_reward
            )

        position_size = getattr(
            decision,
            "position_size",
            None,
        )

        if position_size is None:

            position_size = getattr(
                execution_policy,
                "position_size",
                None,
            )

        if position_size is None:

            position_size = ""

        else:

            position_size = str(
                position_size
            )

        holding_type = getattr(
            decision,
            "holding_type",
            None,
        )

        if holding_type is None:

            holding_type = getattr(
                execution_policy,
                "holding_type",
                None,
            )

        if holding_type is None:

            holding_type = ""

        else:

            holding_type = str(
                holding_type
            )

        risk = getattr(
            decision,
            "risk",
            None,
        )

        if risk is None:

            risk = getattr(
                execution_policy,
                "risk",
                None,
            )

        if risk is None:

            risk = ""

        else:

            risk = str(
                risk
            )

        #
        # Return the existing TradePlan contract.
        #

        return TradePlan(

            recommendation=(
                recommendation.recommendation
            ),

            confidence=(
                recommendation.confidence
            ),

            trade_quality=(
                trade_quality
            ),

            entry_price=(
                recommendation.entry_price
            ),

            stop_loss=(
                recommendation.stop_loss
            ),

            target1=(
                target1
            ),

            target2=(
                target2
            ),

            risk_reward=(
                risk_reward
            ),

            position_size=(
                position_size
            ),

            holding_type=(
                holding_type
            ),

            risk=(
                risk
            ),

            reasons=(
                recommendation.reasons
            ),
        )
