"""
============================================================

RUSI Trader AI

Execution Validation Result

============================================================
"""

from dataclasses import dataclass


@dataclass
class ExecutionValidationResult:

    approved: bool

    reason: str

    confidence_ok: bool

    market_open: bool

    risk_ok: bool

    margin_ok: bool

    cooldown_ok: bool

    daily_limit_ok: bool

    position_ok: bool
