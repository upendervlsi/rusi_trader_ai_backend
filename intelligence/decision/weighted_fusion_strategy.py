"""
========================================================================

RUSI Trader AI

Weighted Fusion Strategy

========================================================================
"""

from __future__ import annotations

from intelligence.decision.decision_config import DecisionConfig
from intelligence.decision.evidence_fusion import (
    EvidenceFusion,
    FusionResult,
)
from intelligence.decision.fusion_strategy import FusionStrategy
from intelligence.evidence.evidence import Evidence


class WeightedFusionStrategy(FusionStrategy):

    def __init__(
        self,
        config: DecisionConfig,
    ):

        self._config = config

    def fuse(
        self,
        evidences: list[Evidence],
    ) -> FusionResult:

        return EvidenceFusion.fuse(
            evidences,
            self._config.feature_weights,
        )
