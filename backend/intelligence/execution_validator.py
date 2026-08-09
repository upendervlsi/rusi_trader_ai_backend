"""
============================================================

RUSI Trader AI

Execution Validator

============================================================
"""

from .execution_validation_result import (
    ExecutionValidationResult,
)


class ExecutionValidator:

    MIN_CONFIDENCE = 70.0

    def validate(

        self,

        trade_plan,

        runtime=None,

    ) -> ExecutionValidationResult:

        #
        # Confidence
        #

        confidence_ok = (

            trade_plan.confidence >=

            self.MIN_CONFIDENCE

        )

        #
        # Market
        #

        market_open = True

        #
        # Risk
        #

        risk_ok = True

        #
        # Margin
        #

        margin_ok = True

        #
        # Cooldown
        #

        cooldown_ok = True

        #
        # Daily Limit
        #

        daily_limit_ok = True

        #
        # Position
        #

        position_ok = True

        approved = (

            confidence_ok

            and market_open

            and risk_ok

            and margin_ok

            and cooldown_ok

            and daily_limit_ok

            and position_ok

        )

        if approved:

            reason = "Execution Approved"

        elif not confidence_ok:

            reason = (

                "Confidence below threshold"

            )

        else:

            reason = "Execution Blocked"

        return ExecutionValidationResult(

            approved=approved,

            reason=reason,

            confidence_ok=confidence_ok,

            market_open=market_open,

            risk_ok=risk_ok,

            margin_ok=margin_ok,

            cooldown_ok=cooldown_ok,

            daily_limit_ok=daily_limit_ok,

            position_ok=position_ok,

        )
