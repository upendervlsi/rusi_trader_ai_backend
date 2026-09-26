"""
============================================================

RUSI Trader AI

Runtime API

Exposes the authoritative Trading Runtime state.

This API only reads RuntimeManager.
It does not communicate with the broker.

============================================================
"""

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from fastapi import APIRouter

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)


router = APIRouter(
    prefix="/api",
    tags=["Runtime"],
)


facade = TradingEngineFacade()


# ============================================================
# Serialization Helper
# ============================================================

def _serialize(value: Any):

    if value is None:
        return None

    # --------------------------------------------------------
    # Primitive values
    # --------------------------------------------------------

    if isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    # --------------------------------------------------------
    # Enum
    # --------------------------------------------------------

    if isinstance(value, Enum):
        return value.value

    # --------------------------------------------------------
    # Dataclass
    # --------------------------------------------------------

    if is_dataclass(value):

        return {
            key: _serialize(item)
            for key, item in asdict(value).items()
        }

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(value, dict):

        return {
            str(key): _serialize(item)
            for key, item in value.items()
        }

    # --------------------------------------------------------
    # List / Tuple / Set
    # --------------------------------------------------------

    if isinstance(
        value,
        (list, tuple, set),
    ):

        return [
            _serialize(item)
            for item in value
        ]

    # --------------------------------------------------------
    # Objects with __dict__
    # --------------------------------------------------------

    if hasattr(value, "__dict__"):

        return {
            key: _serialize(item)
            for key, item in vars(value).items()
        }

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return str(value)


# ============================================================
# Runtime State
# ============================================================

@router.get("/runtime/state")
def get_runtime_state():

    state = facade.get_runtime_state()

    return {
        "cycle_id": state.cycle_id,
        "updated_time": state.updated_time,
        "data_status": state.data_status,

        "instrument": _serialize(
            state.instrument
        ),

        "live_price": state.live_price,

        "snapshot": _serialize(
            state.snapshot
        ),

        "feature_store": _serialize(
            state.feature_store
        ),

        "evidence": _serialize(
            state.evidence
        ),

        "intelligence": _serialize(
            state.intelligence
        ),

        "decision": _serialize(
            state.decision
        ),

        "recommendation": _serialize(
            state.recommendation
        ),

        "suggestions": _serialize(
            state.suggestions
        ),

        "execution_policy": _serialize(
            state.execution_policy
        ),

        "order": _serialize(
            state.order
        ),

        "risk_result": _serialize(
            state.risk_result
        ),

        "broker_result": _serialize(
            state.broker_result
        ),

        "position": _serialize(
            state.position
        ),

        "portfolio": _serialize(
            state.portfolio
        ),

        "portfolio_summary": _serialize(
            state.portfolio_summary
        ),
    }
