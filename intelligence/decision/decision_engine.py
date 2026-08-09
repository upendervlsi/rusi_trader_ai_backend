"""
========================================================================

Decision Engine

========================================================================
"""

from __future__ import annotations

from typing import Iterable

from intelligence.decision.decision_config import DecisionConfig
from intelligence.decision.decision_result import DecisionResult
from intelligence.decision.evidence_fusion import EvidenceFusion
from intelligence.decision.weighted_fusion_strategy import (
    WeightedFusionStrategy,
)
from intelligence.evidence.evidence import Evidence
from intelligence.signals.signal_type import SignalType


class DecisionEngine:

    def __init__(
        self,
        config: DecisionConfig | None = None,
    ):

        self._config = config or DecisionConfig()
        self._fusion_strategy = WeightedFusionStrategy(
            self._config
        )

    def decide(
        self,
        evidences: Iterable[Evidence],
    ) -> DecisionResult:

        evidences = list(evidences)

        fusion = self._fusion_strategy.fuse(
            evidences
        )

        if fusion.score >= self._config.buy_threshold:

            signal = SignalType.BUY

        elif fusion.score <= self._config.sell_threshold:

            signal = SignalType.SELL

        else:

            signal = SignalType.HOLD

        return DecisionResult(
            signal=signal,
            confidence=fusion.confidence,
            evidences=evidences,
            summary=(
                f"Weighted score = "
                f"{fusion.score:.3f}"
            ),
        )
