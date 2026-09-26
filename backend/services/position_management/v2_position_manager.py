"""
RUSI Trader AI
V2 Paper Position Management

Position-management layer only.

This module does NOT generate trading signals.
It consumes the existing RUSI recommendation/runtime state
and decides whether an existing paper position should remain
open or be exited.

V1 hard SL and target remain the final safety backstop.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class V2PositionDecision:
    action: str
    reason: str
    current_move_pct: float
    mfe_pct: float
    mae_pct: float
    recommendation: str
    confidence: float
    score: float


class V2PositionManager:

    # =========================================================
    # MASTER SWITCH
    # =========================================================

    ENABLED = True

    # =========================================================
    # EARLY LOSS MANAGEMENT
    # =========================================================

    # We do NOT replace the V1 -25% hard stop.
    #
    # This is only an early-exit candidate when the RUSI
    # underlying thesis has actually reversed.

    EARLY_LOSS_THRESHOLD_PCT = -12.0

    # Do not act on a weak/low-confidence opposite signal.

    EARLY_LOSS_MIN_CONFIDENCE = 60.0

    # =========================================================
    # PROFIT PROTECTION
    # =========================================================

    # Protection becomes eligible after meaningful MFE.

    PROFIT_PROTECTION_ARM_PCT = 15.0

    # Protect after 30% of the favorable excursion is given back.

    PROFIT_GIVEBACK_FRACTION = 0.30

    # Never close a profit-protection trade below this profit
    # floor unless V1 hard SL/target handles it.

    MIN_PROTECTED_PROFIT_PCT = 5.0

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:
            if value is None:
                return default

            return float(value)

        except (TypeError, ValueError):

            return default

    @classmethod
    def _recommendation_values(
        cls,
        recommendation: Any,
    ):

        if recommendation is None:

            return (
                "UNKNOWN",
                0.0,
                0.0,
            )

        signal = str(
            getattr(
                recommendation,
                "recommendation",
                "",
            )
        ).upper()

        confidence = cls._number(
            getattr(
                recommendation,
                "confidence",
                0.0,
            )
        )

        score = cls._number(
            getattr(
                recommendation,
                "score",
                0.0,
            )
        )

        return (
            signal,
            confidence,
            score,
        )

    @staticmethod
    def _original_underlying_signal(
        trade: Any,
    ) -> str:

        option_type = str(
            getattr(
                trade,
                "option_type",
                "",
            )
        ).upper()

        #
        # RUSI option-buying convention:
        #
        # CE -> bullish underlying thesis -> BUY
        # PE -> bearish underlying thesis -> SELL
        #

        if option_type == "CE":
            return "BUY"

        if option_type == "PE":
            return "SELL"

        #
        # Fallback for old/unknown records.
        #

        reason = str(
            getattr(
                trade,
                "reason",
                "",
            )
        ).upper()

        if "UNDERLYINGSIGNAL=SELL" in reason:
            return "SELL"

        if "UNDERLYINGSIGNAL=BUY" in reason:
            return "BUY"

        return "UNKNOWN"

    @classmethod
    def evaluate(
        cls,
        trade: Any,
        current_price: float,
        mfe_pct: float,
        mae_pct: float,
        recommendation: Any = None,
    ) -> V2PositionDecision:

        entry_price = cls._number(
            getattr(
                trade,
                "entry_price",
                0.0,
            )
        )

        if entry_price <= 0:

            return V2PositionDecision(
                action="HOLD",
                reason="Invalid entry price",
                current_move_pct=0.0,
                mfe_pct=mfe_pct,
                mae_pct=mae_pct,
                recommendation="UNKNOWN",
                confidence=0.0,
                score=0.0,
            )

        current_move_pct = (
            (
                current_price
                - entry_price
            )
            / entry_price
        ) * 100.0

        (
            current_signal,
            confidence,
            score,
        ) = cls._recommendation_values(
            recommendation
        )

        if not cls.ENABLED:

            return V2PositionDecision(
                action="HOLD",
                reason="V2 disabled",
                current_move_pct=current_move_pct,
                mfe_pct=mfe_pct,
                mae_pct=mae_pct,
                recommendation=current_signal,
                confidence=confidence,
                score=score,
            )

        #
        # -------------------------------------------------------
        # ORIGINAL UNDERLYING THESIS
        # -------------------------------------------------------
        #

        original_signal = (
            cls._original_underlying_signal(
                trade
            )
        )

        thesis_reversed = (
            (
                original_signal == "BUY"
                and current_signal == "SELL"
            )
            or
            (
                original_signal == "SELL"
                and current_signal == "BUY"
            )
        )

        #
        # -------------------------------------------------------
        # EARLY LOSS EXIT
        # -------------------------------------------------------
        #
        # Requirements:
        #
        # 1. Option is down at least 12%.
        # 2. Current RUSI recommendation has reversed.
        # 3. Opposite recommendation has >=60 confidence.
        #
        # This is intentionally much more selective than simply
        # using a tighter stop.
        #

        if (
            current_move_pct
            <= cls.EARLY_LOSS_THRESHOLD_PCT
            and thesis_reversed
            and confidence
            >= cls.EARLY_LOSS_MIN_CONFIDENCE
        ):

            return V2PositionDecision(
                action="EARLY_LOSS_EXIT",
                reason=(
                    "Option loss reached V2 early-loss threshold "
                    "and the underlying RUSI thesis reversed "
                    "with sufficient confidence"
                ),
                current_move_pct=current_move_pct,
                mfe_pct=mfe_pct,
                mae_pct=mae_pct,
                recommendation=current_signal,
                confidence=confidence,
                score=score,
            )

        #
        # -------------------------------------------------------
        # PROFIT PROTECTION
        # -------------------------------------------------------
        #

        if mfe_pct >= cls.PROFIT_PROTECTION_ARM_PCT:

            giveback_limit = (
                mfe_pct
                * cls.PROFIT_GIVEBACK_FRACTION
            )

            protected_floor = max(
                cls.MIN_PROTECTED_PROFIT_PCT,
                mfe_pct - giveback_limit,
            )

            if (
                current_move_pct
                <= protected_floor
                and current_move_pct > 0
            ):

                return V2PositionDecision(
                    action="PROFIT_PROTECTION_EXIT",
                    reason=(
                        "Meaningful MFE was achieved and "
                        "the position retraced enough to "
                        "protect remaining profit"
                    ),
                    current_move_pct=current_move_pct,
                    mfe_pct=mfe_pct,
                    mae_pct=mae_pct,
                    recommendation=current_signal,
                    confidence=confidence,
                    score=score,
                )

        return V2PositionDecision(
            action="HOLD",
            reason="V2 conditions not triggered",
            current_move_pct=current_move_pct,
            mfe_pct=mfe_pct,
            mae_pct=mae_pct,
            recommendation=current_signal,
            confidence=confidence,
            score=score,
        )
