"""
============================================================

RUSI Trader AI

Simple Decision Rule

V1 Weighted Evidence Decision Policy

============================================================
"""

from __future__ import annotations

from common.logger import get_logger

from intelligence.decision.decision import Decision
from intelligence.decision.decision_config import DecisionConfig
from intelligence.decision.decision_rule import DecisionRule
from intelligence.decision.weighted_fusion_strategy import (
    WeightedFusionStrategy,
)
from intelligence.evidence.evidence_context import EvidenceContext
from intelligence.signals.signal_type import SignalType


logger = get_logger("RUSI")


class SimpleDecisionRule(DecisionRule):

    def __init__(
        self,
        config: DecisionConfig | None = None,
    ) -> None:

        self._config = (
            config
            if config is not None
            else DecisionConfig()
        )

        self._fusion = WeightedFusionStrategy(
            self._config
        )

    @property
    def name(self) -> str:

        return "Simple Decision Rule"

    def evaluate(
        self,
        evidence: EvidenceContext,
    ) -> Decision:

        #
        # ---------------------------------------------------------
        # No evidence
        # ---------------------------------------------------------
        #

        if not evidence.evidences:

            logger.info(
                "Decision Evidence : No evidence available"
            )

            return Decision(
                signal=SignalType.HOLD,
                confidence=0.0,
                score=0.0,
                reasons=[
                    "No evidence available"
                ],
            )

        #
        # ---------------------------------------------------------
        # Evidence reasons
        # ---------------------------------------------------------
        #

        reasons: list[str] = []

        for item in evidence.evidences:

            reasons.append(
                f"{item.feature_id.name} -> "
                f"{item.signal.name} "
                f"({item.confidence:.2f})"
            )

        #
        # ---------------------------------------------------------
        # Weighted Evidence Fusion
        # ---------------------------------------------------------
        #

        fusion = self._fusion.fuse(
            evidence.evidences
        )

        score = fusion.score

        #
        # ---------------------------------------------------------
        # Directional confidence
        # ---------------------------------------------------------
        #
        # Confidence represents the percentage of weighted
        # evidence supporting the selected direction.
        #
        # Example:
        #
        # BUY  = 145
        # SELL = 80
        #
        # BUY confidence =
        #
        #     145 / (145 + 80) * 100
        #
        # This is intentionally calculated here rather than
        # changing EvidenceFusion or the execution pipeline.
        #

        bullish_weight = 0.0
        bearish_weight = 0.0

        for item in evidence.evidences:

            weight = self._config.feature_weights.get(
                item.feature_id,
                1.0,
            )

            contribution = (
                item.confidence
                * weight
            )

            if item.signal == SignalType.BUY:

                bullish_weight += contribution

            elif item.signal == SignalType.SELL:

                bearish_weight += contribution

        directional_total = (
            bullish_weight
            + bearish_weight
        )

        #
        # ---------------------------------------------------------
        # Directional Decision
        # ---------------------------------------------------------
        #

        if score >= self._config.buy_threshold:

            signal = SignalType.BUY

        elif score <= self._config.sell_threshold:

            signal = SignalType.SELL

        else:

            signal = SignalType.HOLD

        #
        # ---------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------
        #

        if signal == SignalType.BUY:

            confidence = (
                bullish_weight
                / directional_total
                * 100.0
                if directional_total > 0
                else 0.0
            )

        elif signal == SignalType.SELL:

            confidence = (
                bearish_weight
                / directional_total
                * 100.0
                if directional_total > 0
                else 0.0
            )

        else:

            confidence = 0.0

        confidence = min(
            confidence,
            100.0,
        )

        #
        # ---------------------------------------------------------
        # Logging
        # ---------------------------------------------------------
        #

        logger.info(
            "Decision Evidence : Count=%d",
            len(evidence.evidences),
        )

        logger.info(
            "Decision Evidence : "
            "Bullish=%.2f | Bearish=%.2f",
            bullish_weight,
            bearish_weight,
        )

        logger.info(
            "Decision Fusion   : "
            "Score=%.4f | Confidence=%.2f",
            score,
            confidence,
        )

        logger.info(
            "Decision Generated : "
            "%s | Score=%.2f | Confidence=%.2f",
            signal.name,
            score,
            confidence,
        )

        for reason in reasons:

            logger.info(
                "Decision Reason : %s",
                reason,
            )

        return Decision(
            signal=signal,
            confidence=confidence,
            score=score,
            reasons=reasons,
        )
