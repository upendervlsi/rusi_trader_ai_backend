"""
RUSI Trader AI

Suggestion Manager

Maintains AI-generated trading suggestions and their
lifecycle.

This manager does NOT execute broker orders.

Confidence <= 50% suggestions are ignored.

Suggestions remain active until the lifecycle determines
that the opportunity has completed.
"""

from datetime import datetime

from trading.suggestions.suggestion import TradingSuggestion


class SuggestionManager:

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    MIN_CONFIDENCE = 50.0

    REVERSAL_CONFIRMATIONS = 3

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def __init__(self):

        self._suggestions: dict[
            str,
            TradingSuggestion,
        ] = {}

    # =========================================================
    # PUBLISH
    # =========================================================

    def publish(
        self,
        suggestion: TradingSuggestion,
    ) -> None:

        #
        # User rule:
        #
        # <= 50% => ignore
        #

        if suggestion.confidence <= self.MIN_CONFIDENCE:

            return

        #
        # Only actionable directions are allowed.
        #

        if suggestion.signal.upper() not in (
            "BUY",
            "SELL",
        ):

            return

        #
        # Stable identity.
        #

        if not suggestion.suggestion_id:

            identity = (
                suggestion.option_symbol
                if suggestion.option_symbol
                else suggestion.symbol
            )

            suggestion.suggestion_id = (
                f"{suggestion.exchange}_"
                f"{identity}"
            )

        now = datetime.now().isoformat()

        existing = self._suggestions.get(
            suggestion.suggestion_id
        )

        #
        # Existing suggestion:
        #
        # Preserve lifecycle information.
        #

        if existing is not None:

            suggestion.created_time = (
                existing.created_time
            )

            suggestion.status = (
                existing.status
            )

            suggestion.entry_reached = (
                existing.entry_reached
            )

            suggestion.entry_reached_price = (
                existing.entry_reached_price
            )

            suggestion.profit_booked = (
                existing.profit_booked
            )

            suggestion.exit_reason = (
                existing.exit_reason
            )

            suggestion.exit_price = (
                existing.exit_price
            )

            suggestion.reversal_warning = (
                existing.reversal_warning
            )

            suggestion.reversal_count = (
                existing.reversal_count
            )

            suggestion.reversal_started_time = (
                existing.reversal_started_time
            )

        else:

            suggestion.created_time = (
                suggestion.created_time
                or now
            )

            suggestion.status = "WATCHING"

        suggestion.updated_time = now

        self._suggestions[
            suggestion.suggestion_id
        ] = suggestion

    # =========================================================
    # PRICE UPDATE
    # =========================================================

    def update_price(
        self,
        suggestion_id: str,
        current_price: float,
    ) -> TradingSuggestion | None:

        suggestion = self._suggestions.get(
            suggestion_id
        )

        if suggestion is None:

            return None

        if current_price <= 0:

            return suggestion

        now = datetime.now().isoformat()

        suggestion.latest_price = current_price

        suggestion.last_checked_price = current_price

        suggestion.last_checked_time = now

        signal = suggestion.signal.upper()

        # -----------------------------------------------------
        # WATCHING
        # -----------------------------------------------------

        if suggestion.status == "WATCHING":

            if self._entry_reached(
                suggestion,
                current_price,
            ):

                suggestion.entry_reached = True

                suggestion.entry_reached_price = (
                    current_price
                )

                suggestion.status = "ACTIVE"

        # -----------------------------------------------------
        # ACTIVE
        # -----------------------------------------------------

        elif suggestion.status in (
            "ACTIVE",
            "PROFIT_ZONE",
            "REVERSAL_WARNING",
        ):

            #
            # Stop loss always has priority.
            #

            if self._stop_loss_reached(
                suggestion,
                current_price,
            ):

                suggestion.status = "EXITED_SL"

                suggestion.exit_price = (
                    current_price
                )

                suggestion.exit_reason = (
                    "STOP_LOSS_REACHED"
                )

                return suggestion

            #
            # Target reached.
            #

            if self._target_reached(
                suggestion,
                current_price,
            ):

                suggestion.profit_booked = True

                suggestion.status = "EXITED_TARGET"

                suggestion.exit_price = (
                    current_price
                )

                suggestion.exit_reason = (
                    "TARGET_REACHED"
                )

                return suggestion

            #
            # If price is moving into profit,
            # explicitly mark the profit zone.
            #

            if self._profit_zone(
                suggestion,
                current_price,
            ):

                suggestion.status = "PROFIT_ZONE"

        suggestion.updated_time = now

        return suggestion

    # =========================================================
    # REVERSAL WARNING
    # =========================================================

    def update_reversal(
        self,
        suggestion_id: str,
        reversal_detected: bool,
    ) -> TradingSuggestion | None:

        suggestion = self._suggestions.get(
            suggestion_id
        )

        if suggestion is None:

            return None

        #
        # Only active/profit trades need reversal
        # monitoring.
        #

        if not suggestion.entry_reached:

            return suggestion

        if suggestion.status not in (
            "ACTIVE",
            "PROFIT_ZONE",
            "REVERSAL_WARNING",
        ):

            return suggestion

        now = datetime.now().isoformat()

        if not reversal_detected:

            #
            # Trend recovered.
            #

            suggestion.reversal_warning = False

            suggestion.reversal_count = 0

            suggestion.reversal_started_time = ""

            if suggestion.profit_booked:

                suggestion.status = "PROFIT_ZONE"

            else:

                suggestion.status = "ACTIVE"

            suggestion.updated_time = now

            return suggestion

        #
        # Reversal detected.
        #

        suggestion.reversal_warning = True

        suggestion.reversal_count += 1

        if not suggestion.reversal_started_time:

            suggestion.reversal_started_time = now

        suggestion.status = "REVERSAL_WARNING"

        #
        # Do NOT immediately exit.
        #
        # Give the market several confirmations.
        #

        if (
            suggestion.reversal_count
            >= self.REVERSAL_CONFIRMATIONS
        ):

            suggestion.status = (
                "EXITED_REVERSAL"
            )

            suggestion.exit_price = (
                suggestion.latest_price
            )

            suggestion.exit_reason = (
                "CONFIRMED_TREND_REVERSAL"
            )

        suggestion.updated_time = now

        return suggestion

    # =========================================================
    # ENTRY
    # =========================================================

    @staticmethod
    def _entry_reached(
        suggestion: TradingSuggestion,
        price: float,
    ) -> bool:

        if suggestion.entry_price <= 0:

            return False

        signal = suggestion.signal.upper()

        if signal == "BUY":

            return price >= suggestion.entry_price

        if signal == "SELL":

            return price <= suggestion.entry_price

        return False

    # =========================================================
    # STOP LOSS
    # =========================================================

    @staticmethod
    def _stop_loss_reached(
        suggestion: TradingSuggestion,
        price: float,
    ) -> bool:

        if suggestion.stop_loss <= 0:

            return False

        signal = suggestion.signal.upper()

        if signal == "BUY":

            return price <= suggestion.stop_loss

        if signal == "SELL":

            return price >= suggestion.stop_loss

        return False

    # =========================================================
    # TARGET
    # =========================================================

    @staticmethod
    def _target_reached(
        suggestion: TradingSuggestion,
        price: float,
    ) -> bool:

        if suggestion.target_price <= 0:

            return False

        signal = suggestion.signal.upper()

        if signal == "BUY":

            return price >= suggestion.target_price

        if signal == "SELL":

            return price <= suggestion.target_price

        return False

    # =========================================================
    # PROFIT ZONE
    # =========================================================

    @staticmethod
    def _profit_zone(
        suggestion: TradingSuggestion,
        price: float,
    ) -> bool:

        if (
            suggestion.entry_price <= 0
            or suggestion.target_price <= 0
        ):

            return False

        signal = suggestion.signal.upper()

        #
        # First half of the entry-to-target distance.
        #

        midpoint = (
            suggestion.entry_price
            + (
                suggestion.target_price
                - suggestion.entry_price
            ) * 0.5
        )

        if signal == "BUY":

            return price >= midpoint

        if signal == "SELL":

            return price <= midpoint

        return False

    # =========================================================
    # GET ACTIVE
    # =========================================================

    def get_active(
        self,
    ) -> list[TradingSuggestion]:

        #
        # Keep all suggestions that have not completed.
        #

        active_statuses = (
            "WATCHING",
            "ENTRY_REACHED",
            "ACTIVE",
            "PROFIT_ZONE",
            "REVERSAL_WARNING",
        )

        return [
            suggestion
            for suggestion
            in self._suggestions.values()
            if suggestion.status
            in active_statuses
        ]

    # =========================================================
    # GET ALL
    # =========================================================

    def get_all(
        self,
    ) -> list[TradingSuggestion]:

        return list(
            self._suggestions.values()
        )

    # =========================================================
    # GET ONE
    # =========================================================

    def get(
        self,
        suggestion_id: str,
    ) -> TradingSuggestion | None:

        return self._suggestions.get(
            suggestion_id
        )

    # =========================================================
    # REMOVE
    # =========================================================

    def remove(
        self,
        suggestion_id: str,
    ) -> None:

        self._suggestions.pop(
            suggestion_id,
            None,
        )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self) -> None:

        self._suggestions.clear()
