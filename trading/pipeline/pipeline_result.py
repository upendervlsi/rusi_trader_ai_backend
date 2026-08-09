"""
========================================================================

RUSI Trader AI

Pipeline Result

========================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineResult:
    """
    Result of executing one pipeline stage.
    """

    stage_name: str

    success: bool

    message: str = ""

    execution_time_ms: float = 0.0
