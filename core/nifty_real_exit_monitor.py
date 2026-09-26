from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from execution.position_manager.position import Position
from execution.position_manager.position_status import PositionStatus


logger = logging.getLogger(__name__)


class NiftyRealExitMonitor:
    """
    NIFTY F&O real-trading exit decision and execution coordinator.

    IMPORTANT:
    - NIFTY_FNO real trading only.
    - Never used by Paper Trading.
    - Never used by MIDCAP, MCX, or Stock Options.
    - Broker SELL confirmation is required before a local position
      is marked CLOSED.
    """

    def __init__(
        self,
        *,
        market_data_engine,
        order_executor,
        pending_exit_store,
        trading_config,
    ):
        self._market_data_engine = market_data_engine
        self._order_executor = order_executor
        self._pending_exit_store = pending_exit_store
        self._trading_config = trading_config

    def evaluate_exit_reason(
        self,
        position: Position,
        decision=None,
    ) -> Optional[str]:
        """
        Evaluate the existing RUSI exit rules without changing them.

        Priority:
        1. Profit Protection
        2. Confirmed Market Reversal
        3. Stop Loss
        4. Target

        This method NEVER places a broker order.
        """

        if position.status != PositionStatus.OPEN:
            return None

        symbol = str(
            getattr(position, "symbol", "") or ""
        ).strip()

        if (
            not symbol.startswith("NIFTY")
            or symbol.startswith("MIDCPNIFTY")
        ):
            return None

        live_price = self._market_data_engine.get_instrument_ltp(
            exchange=position.exchange,
            symbol=position.symbol,
            token=position.token,
        )

        if live_price is None:
            logger.warning(
                "NIFTY Real Exit Monitor : "
                "Live option LTP unavailable | Symbol=%s",
                position.symbol,
            )
            return None

        try:
            # MarketDataEngine returns LiveMarketData for broker LTP
            # requests. Extract the numeric last_price before conversion.
            # Preserve compatibility with plain numeric values.
            if hasattr(live_price, "last_price"):
                current_price = float(live_price.last_price)
            elif isinstance(live_price, dict):
                current_price = float(
                    live_price.get("last_price", live_price.get("ltp"))
                )
            else:
                current_price = float(live_price)

        except (TypeError, ValueError, AttributeError):
            logger.warning(
                "NIFTY Real Exit Monitor : "
                "Invalid live option LTP | Symbol=%s | LTP=%s",
                position.symbol,
                live_price,
            )
            return None

        if current_price <= 0:
            logger.warning(
                "NIFTY Real Exit Monitor : "
                "Invalid live option LTP | Symbol=%s | LTP=%.4f",
                position.symbol,
                current_price,
            )
            return None

        position.current_price = current_price

        position.unrealized_pnl = (
            current_price - position.entry_price
        ) * position.quantity

        if current_price > position.highest_price:
            position.highest_price = current_price

        if (
            position.unrealized_pnl
            > position.highest_unrealized_pnl
        ):
            position.highest_unrealized_pnl = (
                position.unrealized_pnl
            )

        logger.info(
            "NIFTY Real Exit Monitor : "
            "Position=%s | Symbol=%s | Entry=%.2f | "
            "Current=%.2f | Qty=%d | UnrealizedPnL=%.2f",
            position.position_id,
            position.symbol,
            position.entry_price,
            current_price,
            position.quantity,
            position.unrealized_pnl,
        )

        #
        # 1. Profit Protection
        #
        activation_percent = float(
            getattr(
                self._trading_config,
                "profit_protection_activation_percent",
                10.0,
            )
        )

        retrace_percent = float(
            getattr(
                self._trading_config,
                "profit_protection_retrace_percent",
                50.0,
            )
        )

        activation_price = (
            position.entry_price
            * (1.0 + activation_percent / 100.0)
        )

        if (
            position.highest_price >= activation_price
            and position.highest_price > position.entry_price
        ):
            protected_price = (
                position.entry_price
                + (
                    position.highest_price
                    - position.entry_price
                )
                * (retrace_percent / 100.0)
            )

            position.protected_price = max(
                position.protected_price,
                protected_price,
            )

            position.profit_protection_active = True

            logger.info(
                "NIFTY Real Exit Monitor : "
                "Profit Protection Active | "
                "Symbol=%s | Peak=%.2f | Protected=%.2f | "
                "Current=%.2f",
                position.symbol,
                position.highest_price,
                position.protected_price,
                current_price,
            )

            if current_price <= position.protected_price:
                return "PROFIT_PROTECTION"

        #
        # 2. Confirmed Market Reversal
        #
        signal_name = ""
        confidence = 0.0

        if decision is not None:
            signal = getattr(decision, "signal", None)

            signal_name = str(
                getattr(
                    signal,
                    "name",
                    signal or "",
                )
            ).strip().upper()

            try:
                confidence = float(
                    getattr(
                        decision,
                        "confidence",
                        0.0,
                    )
                )
            except (TypeError, ValueError):
                confidence = 0.0

        option_type = ""
        upper_symbol = symbol.upper()

        if upper_symbol.endswith("CE"):
            option_type = "CE"
        elif upper_symbol.endswith("PE"):
            option_type = "PE"

        alignment_reversed = (
            (option_type == "CE" and signal_name == "SELL")
            or
            (option_type == "PE" and signal_name == "BUY")
        )

        reversal_confidence = float(
            getattr(
                self._trading_config,
                "reversal_confirmation_confidence",
                1.45,
            )
        )

        reversal_cycles = int(
            getattr(
                self._trading_config,
                "reversal_confirmation_cycles",
                2,
            )
        )

        if (
            alignment_reversed
            and confidence >= reversal_confidence
        ):
            previous_signal = str(
                getattr(
                    position,
                    "last_reversal_signal",
                    "",
                )
                or ""
            ).strip().upper()

            if previous_signal == signal_name:
                position.reversal_count += 1
            else:
                position.reversal_count = 1
                position.last_reversal_signal = signal_name

            logger.info(
                "NIFTY Real Exit Monitor : "
                "Reversal Confirmation | "
                "Symbol=%s | Signal=%s | Confidence=%.2f | "
                "Count=%d/%d",
                position.symbol,
                signal_name,
                confidence,
                position.reversal_count,
                reversal_cycles,
            )

            if position.reversal_count >= reversal_cycles:
                return "CONFIRMED_MARKET_REVERSAL"

        else:
            position.reversal_count = 0
            position.last_reversal_signal = ""

        #
        # 3. Hard Stop Loss
        #
        if (
            position.stop_loss > 0
            and current_price <= position.stop_loss
        ):
            return "STOP_LOSS"

        #
        # 4. Target
        #
        if (
            position.target_price > 0
            and current_price >= position.target_price
        ):
            return "TARGET"

        return None
