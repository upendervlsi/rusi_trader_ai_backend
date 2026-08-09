"""
============================================================

Decision Context

============================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from intelligence.decision.decision import Decision


@dataclass(slots=True)
class DecisionContext:
    """
    Holds the final decision.
    """

    decision: Decision | None = None
