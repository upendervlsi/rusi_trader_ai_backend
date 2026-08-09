"""
============================================================

RUSI Trader AI

Intelligence API

============================================================
"""

from fastapi import APIRouter

from backend.services.intelligence_service import (
    IntelligenceService,
)

from backend.services.execution_service import (
    ExecutionService,
)

router = APIRouter(

    prefix="/api",

    tags=["Intelligence"],

)

intelligence_service = IntelligenceService()

execution_service = ExecutionService()


@router.get("/intelligence")
def intelligence():

    #
    # AI Trade Plan
    #

    plan = intelligence_service.generate()

    #
    # Execution Validation
    #

    execution = execution_service.validate(

        plan,

    )

    return {

        "trade_plan": {

            "recommendation":
                plan.recommendation,

            "confidence":
                plan.confidence,

            "trade_quality":
                plan.trade_quality,

            "entry_price":
                plan.entry_price,

            "stop_loss":
                plan.stop_loss,

            "target1":
                plan.target1,

            "target2":
                plan.target2,

            "risk_reward":
                plan.risk_reward,

            "position_size":
                plan.position_size,

            "holding_type":
                plan.holding_type,

            "risk":
                plan.risk,

            "reasons":
                plan.reasons,

        },

        "execution": {

            "approved":
                execution.approved,

            "reason":
                execution.reason,

            "confidence_ok":
                execution.confidence_ok,

            "market_open":
                execution.market_open,

            "risk_ok":
                execution.risk_ok,

            "margin_ok":
                execution.margin_ok,

            "cooldown_ok":
                execution.cooldown_ok,

            "daily_limit_ok":
                execution.daily_limit_ok,

            "position_ok":
                execution.position_ok,

        }

    }
