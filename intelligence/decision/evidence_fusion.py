"""
RUSI Trader AI

Evidence Fusion

Combines multiple Evidence objects into a weighted score.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from common.logger import get_logger

from intelligence.evidence.evidence import Evidence
from intelligence.signals.signal_type import SignalType


logger = get_logger("RUSI")


@dataclass(frozen=True, slots=True)
class FusionResult:

    score: float
    confidence: float


class EvidenceFusion:
    """
    Weighted evidence fusion.
    """

    @staticmethod
    def fuse(
        evidences: Iterable[Evidence],
        weights: dict | None = None,
    ) -> FusionResult:

        evidence_list = list(evidences)

        if not evidence_list:

            return FusionResult(
                score=0.0,
                confidence=0.0,
            )

        weights = weights or {}

        weighted_sum = 0.0
        weighted_confidence = 0.0
        total_weight = 0.0

        logger.info(
            "========== EVIDENCE FUSION =========="
        )

        for evidence in evidence_list:

            if evidence.signal == SignalType.BUY:

                direction = 1.0

            elif evidence.signal == SignalType.SELL:

                direction = -1.0

            else:

                direction = 0.0

            weight = weights.get(
                evidence.feature_id,
                1.0,
            )

            logger.info(
                "Evidence : %s | Signal=%s | "
                "Confidence=%.4f | Weight=%.4f",
                evidence.feature_id,
                evidence.signal,
                evidence.confidence,
                weight,
            )

            score = (
                direction
                * evidence.confidence
                * weight
            )

            weighted_sum += score

            weighted_confidence += (
                evidence.confidence
                * weight
            )

            total_weight += weight

        if weighted_confidence == 0:

            normalized_score = 0.0

        else:

            normalized_score = (
                weighted_sum
                / weighted_confidence
            )

        if total_weight == 0:

            confidence = 0.0

        else:

            confidence = (
                weighted_confidence
                / total_weight
            )

        logger.info(
            "Fusion Weighted Sum        : %.6f",
            weighted_sum,
        )

        logger.info(
            "Fusion Weighted Confidence : %.6f",
            weighted_confidence,
        )

        logger.info(
            "Fusion Total Weight        : %.6f",
            total_weight,
        )

        logger.info(
            "Fusion Normalized Score    : %.6f",
            normalized_score,
        )

        logger.info(
            "Fusion Confidence          : %.6f",
            confidence,
        )

        logger.info(
            "===================================="
        )

        return FusionResult(
            score=normalized_score,
            confidence=confidence,
        )
