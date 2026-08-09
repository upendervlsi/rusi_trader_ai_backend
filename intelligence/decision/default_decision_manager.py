"""
============================================================

Default Decision Manager

============================================================
"""

from __future__ import annotations

from intelligence.decision.decision_manager import DecisionManager
from intelligence.decision.rules.simple_decision_rule import (
    SimpleDecisionRule,
)


def build_default_decision_manager() -> DecisionManager:
    """
    Builds the default decision manager.
    """

    return DecisionManager(
        SimpleDecisionRule()
    )
