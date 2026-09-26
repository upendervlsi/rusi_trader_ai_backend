"""
============================================================
RUSI Trader AI

Stock Options Position Exit Service

Stage 8C
============================================================

Purpose
-------
Apply a StockOptionsPositionMonitor EXIT decision to the
shared paper PortfolioEngine.

This module is stock-options specific and does not modify
the NIFTY V1 runtime.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StockOptionsExitResult:
    success: bool
    action: str
    symbol: str
    reason: str
    realized_pnl: float
    message: str


class StockOptionsPositionExitService:

    def __init__(self, portfolio_engine):
        self._portfolio_engine = portfolio_engine

    def apply(self, position, monitor_result) -> StockOptionsExitResult:

        if position is None:
            return StockOptionsExitResult(
                success=False,
                action="NO_EXIT",
                symbol="",
                reason="",
                realized_pnl=0.0,
                message="No position supplied.",
            )

        if monitor_result is None:
            return StockOptionsExitResult(
                success=False,
                action="NO_EXIT",
                symbol=position.symbol,
                reason="",
                realized_pnl=0.0,
                message="No monitor result supplied.",
            )

        if monitor_result.action != "EXIT":
            return StockOptionsExitResult(
                success=True,
                action=monitor_result.action,
                symbol=position.symbol,
                reason=monitor_result.reason,
                realized_pnl=0.0,
                message="Position remains open.",
            )

        closed_position = self._portfolio_engine.close_position(
            position.symbol
        )

        if closed_position is None:
            return StockOptionsExitResult(
                success=False,
                action="EXIT",
                symbol=position.symbol,
                reason=monitor_result.reason,
                realized_pnl=0.0,
                message="Position could not be closed.",
            )

        realized_pnl = float(closed_position.unrealized_pnl)

        return StockOptionsExitResult(
            success=True,
            action="EXIT",
            symbol=position.symbol,
            reason=monitor_result.reason,
            realized_pnl=realized_pnl,
            message="Stock-option paper position closed successfully.",
        )
