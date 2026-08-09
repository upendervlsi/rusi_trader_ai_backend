"""
========================================================================

RUSI Trader AI

Execution Result

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:

    success: bool

    order_id: str

    status: str

    message: str
