"""
============================================================

Candle Verification

============================================================
"""

from common.models import ValidationResult
from market_data.market_snapshot import MarketSnapshot


class CandleVerifier:
    """
    Validates candle integrity.

    This class performs only structural validation.
    Indicator-specific validation belongs to the
    respective intelligence engine.
    """

    def validate(
        self,
        snapshot: MarketSnapshot,
        minimum_candles: int = 1,
    ) -> ValidationResult:

        if snapshot is None:
            return ValidationResult(
                passed=False,
                message="MarketSnapshot is None.",
            )

        if snapshot.candle_count < minimum_candles:
            return ValidationResult(
                passed=False,
                message=(
                    f"Required minimum candles = "
                    f"{minimum_candles}, "
                    f"received = {snapshot.candle_count}"
                ),
            )

        previous_timestamp = None

        for candle in snapshot.candles:

            if candle.high < candle.low:
                return ValidationResult(
                    False,
                    "High price cannot be less than Low price.",
                )

            if candle.volume < 0:
                return ValidationResult(
                    False,
                    "Negative volume detected.",
                )

            if previous_timestamp is not None:

                if candle.timestamp <= previous_timestamp:
                    return ValidationResult(
                        False,
                        "Candles are not in chronological order.",
                    )

            previous_timestamp = candle.timestamp

        return ValidationResult(
            passed=True,
            message="Validation Passed",
        )
