"""
========================================================================

RUSI Trader AI

Decision Summary

Creates a human-readable explanation for decisions.

========================================================================
"""

from __future__ import annotations

from intelligence.decision.decision_result import DecisionResult


class DecisionSummary:

    @staticmethod
    def build(
        decision: DecisionResult,
    ) -> str:

        lines = []

        lines.append(
            f"Final Signal : {decision.signal.name}"
        )

        lines.append(
            f"Confidence   : {decision.confidence:.2f}"
        )

        lines.append("")

        lines.append("Evidence")

        lines.append("----------------")

        for evidence in decision.evidences:

            lines.append(
                f"{evidence.feature_id.name}"
            )

            lines.append(
                f"  Signal     : {evidence.signal.name}"
            )

            lines.append(
                f"  Confidence : "
                f"{evidence.confidence:.2f}"
            )

            lines.append(
                f"  Value      : "
                f"{evidence.value:.4f}"
            )

            lines.append(
                f"  Reason     : "
                f"{evidence.reason}"
            )

            lines.append("")

        lines.append(
            "Engine Summary"
        )

        lines.append("----------------")

        lines.append(
            decision.summary
        )

        return "\n".join(lines)
