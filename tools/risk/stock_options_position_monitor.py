"""
RUSI Trader AI

Stock Options Position Monitor

Stage 8B

Manages an already-open stock-option BUY position.

Responsibilities:
    - Track current premium
    - Track peak premium / peak P&L
    - Apply profit protection
    - Confirm market reversals
    - Check hard stop loss
    - Check target

This module does not fetch market data and does not close the
portfolio position directly.

It does not modify the existing NIFTY V1 position monitor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config.trading_config import TradingConfig


@dataclass(slots=True)
class StockOptionsMonitorResult:
    action: str
    reason: str
    current_price: float
    unrealized_pnl: float
    peak_price: float
    peak_pnl: float
    protected_price: float
    profit_protection_active: bool
    reversal_count: int
    metadata: dict[str, Any]


class StockOptionsPositionMonitor:

    def __init__(
        self,
        trading_config: TradingConfig | None = None,
    ) -> None:
        self._trading_config = (
            trading_config or TradingConfig()
        )

    def monitor(
        self,
        position,
        current_price: float,
        market_direction: str | None = None,
        market_confidence: float = 0.0,
    ) -> StockOptionsMonitorResult:

        current_price = float(current_price)
        market_confidence = float(market_confidence)

        if current_price <= 0:
            return self._result(
                position=position,
                action="HOLD",
                reason="Invalid current option price.",
                current_price=current_price,
            )

        if position.entry_price <= 0:
            return self._result(
                position=position,
                action="HOLD",
                reason="Invalid position entry price.",
                current_price=current_price,
            )

        #
        # BUY-only option position.
        #
        position.current_price = current_price

        #
        # Peak price is stored in metadata so the shared
        # portfolio Position model remains unchanged.
        #
        metadata = position.metadata

        peak_price = float(
            metadata.get(
                "peak_price",
                position.entry_price,
            )
        )

        peak_price = max(
            peak_price,
            current_price,
        )

        metadata["peak_price"] = peak_price

        unrealized_pnl = (
            current_price - position.entry_price
        ) * position.quantity

        peak_pnl = (
            peak_price - position.entry_price
        ) * position.quantity

        metadata["peak_pnl"] = max(
            float(metadata.get("peak_pnl", 0.0)),
            peak_pnl,
        )

        #
        # -----------------------------------------------------
        # PROFIT PROTECTION
        # -----------------------------------------------------
        #

        activation_price = (
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

        protection_active = bool(
            metadata.get(
                "profit_protection_active",
                False,
            )
        )

        protected_price = float(
            metadata.get(
                "protected_price",
                0.0,
            )
        )

        if (
            peak_price >= activation_price
            and peak_price > position.entry_price
        ):

            calculated_protected_price = (
                position.entry_price
                + (
                    peak_price
                    - position.entry_price
                )
                * (
                    self._trading_config
                    .profit_protection_retrace_percent
                    / 100.0
                )
            )

            protected_price = max(
                protected_price,
                calculated_protected_price,
            )

            protection_active = True

            metadata["profit_protection_active"] = True
            metadata["protected_price"] = protected_price

            if current_price <= protected_price:
                return self._result(
                    position=position,
                    action="EXIT",
                    reason="PROFIT_PROTECTION",
                    current_price=current_price,
                    peak_price=peak_price,
                    peak_pnl=metadata["peak_pnl"],
                    protected_price=protected_price,
                    protection_active=True,
                )

        #
        # -----------------------------------------------------
        # CONFIRMED MARKET REVERSAL
        # -----------------------------------------------------
        #

        option_type = self._option_type(
            position
        )

        direction = (
            str(market_direction).upper()
            if market_direction is not None
            else ""
        )

        opposite = (
            (
                option_type == "CE"
                and direction == "BEARISH"
            )
            or
            (
                option_type == "PE"
                and direction == "BULLISH"
            )
        )

        reversal_count = int(
            metadata.get(
                "reversal_count",
                0,
            )
        )

        last_reversal = str(
            metadata.get(
                "last_reversal_signal",
                "",
            )
        )

        if (
            opposite
            and market_confidence
            >= self._trading_config
            .reversal_confirmation_confidence
        ):

            reversal_signal = direction

            if last_reversal == reversal_signal:
                reversal_count += 1
            else:
                reversal_count = 1
                last_reversal = reversal_signal

            metadata["reversal_count"] = reversal_count
            metadata["last_reversal_signal"] = last_reversal

            if (
                reversal_count
                >= self._trading_config
                .reversal_confirmation_cycles
            ):
                return self._result(
                    position=position,
                    action="EXIT",
                    reason="CONFIRMED_MARKET_REVERSAL",
                    current_price=current_price,
                    peak_price=peak_price,
                    peak_pnl=metadata["peak_pnl"],
                    protected_price=protected_price,
                    protection_active=protection_active,
                    reversal_count=reversal_count,
                )

        else:
            metadata["reversal_count"] = 0
            metadata["last_reversal_signal"] = ""

            reversal_count = 0

        #
        # -----------------------------------------------------
        # HARD STOP LOSS
        # -----------------------------------------------------
        #

        if (
            position.stop_loss > 0
            and current_price <= position.stop_loss
        ):
            return self._result(
                position=position,
                action="EXIT",
                reason="STOP_LOSS",
                current_price=current_price,
                peak_price=peak_price,
                peak_pnl=metadata["peak_pnl"],
                protected_price=protected_price,
                protection_active=protection_active,
                reversal_count=reversal_count,
            )

        #
        # -----------------------------------------------------
        # TARGET
        # -----------------------------------------------------
        #

        if (
            position.target_price > 0
            and current_price >= position.target_price
        ):
            return self._result(
                position=position,
                action="EXIT",
                reason="TARGET",
                current_price=current_price,
                peak_price=peak_price,
                peak_pnl=metadata["peak_pnl"],
                protected_price=protected_price,
                protection_active=protection_active,
                reversal_count=reversal_count,
            )

        return self._result(
            position=position,
            action="HOLD",
            reason="Position remains open.",
            current_price=current_price,
            peak_price=peak_price,
            peak_pnl=metadata["peak_pnl"],
            protected_price=protected_price,
            protection_active=protection_active,
            reversal_count=reversal_count,
        )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _option_type(position) -> str:

        symbol = str(
            getattr(position, "symbol", "")
        ).upper()

        if symbol.endswith("CE"):
            return "CE"

        if symbol.endswith("PE"):
            return "PE"

        return ""

    @staticmethod
    def _result(
        position,
        action: str,
        reason: str,
        current_price: float,
        peak_price: float | None = None,
        peak_pnl: float | None = None,
        protected_price: float = 0.0,
        protection_active: bool = False,
        reversal_count: int = 0,
    ) -> StockOptionsMonitorResult:

        if peak_price is None:
            peak_price = float(
                position.metadata.get(
                    "peak_price",
                    position.entry_price,
                )
            )

        if peak_pnl is None:
            peak_pnl = float(
                position.metadata.get(
                    "peak_pnl",
                    0.0,
                )
            )

        unrealized_pnl = (
            current_price - position.entry_price
        ) * position.quantity

        return StockOptionsMonitorResult(
            action=action,
            reason=reason,
            current_price=current_price,
            unrealized_pnl=unrealized_pnl,
            peak_price=peak_price,
            peak_pnl=peak_pnl,
            protected_price=protected_price,
            profit_protection_active=protection_active,
            reversal_count=reversal_count,
            metadata={
                "option_type": StockOptionsPositionMonitor._option_type(
                    position
                ),
            },
        )
