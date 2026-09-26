"""
RUSI Trader AI

Position Monitor

Monitors the currently OPEN paper position.

Responsibilities:
    - Fetch live option LTP
    - Calculate unrealized P&L
    - Check Stop Loss
    - Check Target
    - Close paper position when SL/Target is reached

V1:
    Options are BUY-only.
"""

from datetime import datetime

from common.logger import get_logger

from execution.position_manager.position_status import (
    PositionStatus,
)


logger = get_logger("RUSI")


class PositionMonitor:

    def __init__(
        self,
        position_manager,
        trading_config,
    ):
        self._position_manager = position_manager
        self._trading_config = trading_config

    # =========================================================
    # MONITOR OPEN POSITIONS
    # =========================================================

    def monitor(
        self,
        market_data_engine,
        decision=None,
    ):
        """
        Monitor all currently OPEN positions.

        Returns:
            list of monitored positions.
        """

        positions = (
            self._position_manager
            .registry
            .open_positions()
        )

        if not positions:
            return []

        monitored = []

        for position in positions:
            try:
                self._monitor_position(
                    position,
                    market_data_engine,
                    decision,
                )

                monitored.append(position)

            except Exception as exc:
                logger.exception(
                    "Position Monitoring Failed | "
                    "Position=%s | Error=%s",
                    position.position_id,
                    exc,
                )

        return monitored

    # =========================================================
    # SINGLE POSITION
    # =========================================================

    def _monitor_position(
        self,
        position,
        market_data_engine,
        decision=None,
    ):
        """
        Update one open position using live option LTP.
        """

        live_data = (
            market_data_engine.get_instrument_ltp(
                exchange=position.exchange,
                symbol=position.symbol,
                token=position.token,
            )
        )

        current_price = float(
            live_data.last_price or 0.0
        )

        if current_price <= 0:
            logger.warning(
                "POSITION LTP UNAVAILABLE | "
                "Symbol=%s | Token=%s",
                position.symbol,
                position.token,
            )
            return

        position.current_price = current_price

        #
        # -----------------------------------------------------
        # PROFIT TRACKING
        # -----------------------------------------------------
        #

        if current_price > position.highest_price:
            position.highest_price = current_price

        #
        # V1 is BUY-only.
        #

        position.unrealized_pnl = (
            current_price - position.entry_price
        ) * position.quantity

        #
        # Track the best unrealized P&L reached while the
        # position remains OPEN.
        #

        if (
            position.unrealized_pnl
            > position.highest_unrealized_pnl
        ):
            position.highest_unrealized_pnl = (
                position.unrealized_pnl
            )

        logger.info("")
        logger.info("POSITION STATUS")
        logger.info(
            "Position ID : %s",
            position.position_id,
        )
        logger.info(
            "Symbol      : %s",
            position.symbol,
        )
        logger.info(
            "Entry       : %.2f",
            position.entry_price,
        )
        logger.info(
            "Current LTP : %.2f",
            position.current_price,
        )
        logger.info(
            "Quantity    : %d",
            position.quantity,
        )
        logger.info(
            "P&L         : %.2f",
            position.unrealized_pnl,
        )
        logger.info(
            "Peak Price  : %.2f",
            position.highest_price,
        )
        logger.info(
            "Peak P&L    : %.2f",
            position.highest_unrealized_pnl,
        )
        logger.info(
            "Protection  : %s",
            (
                "ACTIVE"
                if position.profit_protection_active
                else "INACTIVE"
            ),
        )
        logger.info(
            "Protected   : %.2f",
            position.protected_price,
        )
        logger.info(
            "Stop Loss   : %.2f",
            position.stop_loss,
        )
        logger.info(
            "Target      : %.2f",
            position.target_price,
        )
        logger.info(
            "Status      : %s",
            position.status.value,
        )

        # -----------------------------------------------------
        # PROFIT PROTECTION
        # -----------------------------------------------------
        #
        # Once the option has gained 10% from entry, protect
        # 50% of the maximum favorable move.
        #
        # This prevents a profitable trade from unnecessarily
        # returning all the way to the original hard SL.
        #

        profit_activation_price = (
            position.entry_price
            * (
                1.0
                + (
                    self._trading_config
                    .profit_protection_activation_percent
                    / 100.0
                )
            )
        )

        if (
            position.highest_price >= profit_activation_price
            and position.highest_price > position.entry_price
        ):

            protected_price = (
                position.entry_price
                + (
                    position.highest_price
                    - position.entry_price
                )
                * (
                    self._trading_config
                    .profit_protection_retrace_percent
                    / 100.0
                )
            )

            position.protected_price = max(
                position.protected_price,
                protected_price,
            )

            position.profit_protection_active = True

            logger.info(
                "Profit Protection : ACTIVE | "
                "Peak=%.2f | Protected=%.2f",
                position.highest_price,
                position.protected_price,
            )

            if current_price <= position.protected_price:

                self._close_position(
                    position,
                    "PROFIT_PROTECTION",
                )

                return

        # -----------------------------------------------------
        # MARKET ALIGNMENT / CONFIRMED REVERSAL
        # -----------------------------------------------------
        #
        # A single opposite decision is NOT enough to exit.
        #
        # RUSI reassesses the market every cycle. Temporary
        # reversals/noise must not unnecessarily close a trade.
        #
        # V1:
        #
        #   - strong opposite decision
        #   - must persist for 2 consecutive cycles
        #
        # Profit protection and hard SL remain independent
        # safety layers.
        #

        if decision is not None:

            decision_signal = getattr(
                decision.signal,
                "name",
                str(decision.signal),
            )

            decision_confidence = float(
                getattr(
                    decision,
                    "confidence",
                    0.0,
                )
            )

            option_type = (
                "CE"
                if position.symbol.upper().endswith("CE")
                else "PE"
                if position.symbol.upper().endswith("PE")
                else ""
            )

            alignment_reversed = (
                (
                    option_type == "CE"
                    and decision_signal == "SELL"
                )
                or
                (
                    option_type == "PE"
                    and decision_signal == "BUY"
                )
            )

            logger.info(
                "Market Alignment : Option=%s | "
                "Decision=%s | Confidence=%.2f",
                option_type or "UNKNOWN",
                decision_signal,
                decision_confidence,
            )

            #
            # Strong opposite decision.
            #

            if (
                alignment_reversed
                and decision_confidence >= (
                    self._trading_config
                    .reversal_confirmation_confidence
                )
            ):

                #
                # Same opposite signal as previous cycle:
                # increase confirmation count.
                #

                if (
                    position.last_reversal_signal
                    == decision_signal
                ):
                    position.reversal_count += 1

                else:
                    #
                    # First observation of the reversal.
                    #

                    position.reversal_count = 1
                    position.last_reversal_signal = (
                        decision_signal
                    )

                logger.info(
                    "Reversal Confirmation : %d/%d",
                    position.reversal_count,
                    self._trading_config
                    .reversal_confirmation_cycles,
                )

                #
                # Do NOT immediately exit on the first
                # opposite decision.
                #

                if position.reversal_count >= (
                    self._trading_config
                    .reversal_confirmation_cycles
                ):

                    self._close_position(
                        position,
                        "CONFIRMED_MARKET_REVERSAL",
                    )

                    return

            else:

                #
                # Market returned to alignment or reversal
                # became weak.
                #
                # Reset confirmation state.
                #

                if position.reversal_count > 0:

                    logger.info(
                        "Market Reversal Confirmation Reset"
                    )

                position.reversal_count = 0
                position.last_reversal_signal = ""

        # -----------------------------------------------------
        # STOP LOSS
        # -----------------------------------------------------

        if (
            position.stop_loss > 0
            and current_price <= position.stop_loss
        ):
            self._close_position(
                position,
                "STOP_LOSS",
            )
            return

        # -----------------------------------------------------
        # TARGET
        # -----------------------------------------------------

        if (
            position.target_price > 0
            and current_price >= position.target_price
        ):
            self._close_position(
                position,
                "TARGET",
            )
            return

        logger.info(
            "Position remains OPEN"
        )

    # =========================================================
    # PAPER CLOSE
    # =========================================================

    def _close_position(
        self,
        position,
        reason,
    ):
        """
        Close a paper position.

        No broker exit order is sent in this V1 implementation.
        """

        position.realized_pnl = (
            position.unrealized_pnl
        )

        position.exit_time = datetime.now()

        position.exit_reason = reason

        position.status = PositionStatus.CLOSED

        logger.info("")
        logger.info("POSITION CLOSED")
        logger.info(
            "Position ID : %s",
            position.position_id,
        )
        logger.info(
            "Symbol      : %s",
            position.symbol,
        )
        logger.info(
            "Exit Price  : %.2f",
            position.current_price,
        )
        logger.info(
            "Entry Price : %.2f",
            position.entry_price,
        )
        logger.info(
            "Realized P&L: %.2f",
            position.realized_pnl,
        )
        logger.info(
            "Exit Reason : %s",
            reason,
        )
        logger.info(
            "Status      : CLOSED"
        )
