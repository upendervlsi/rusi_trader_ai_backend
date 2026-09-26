"""
============================================================
RUSI Trader AI

Stock Options Paper Runtime

Stage 7A
============================================================

Purpose
-------
Execute one already-selected stock-option candidate in paper
mode using the shared order and portfolio infrastructure.

This module does NOT modify the NIFTY V1 runtime.

The candidate must already have been produced by the
StockOptionCandidateDecisionEngine.

No stock, strike, expiry, or lot size is hardcoded.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from tools.execution.order_models import (
    OrderRequest,
    OrderSide,
)
from tools.portfolio.portfolio_models import Position
from tools.risk.stock_options_risk_engine import StockOptionsRiskEngine


@dataclass(slots=True)
class StockOptionsPaperTradeResult:
    success: bool
    decision: str
    symbol: str
    option_symbol: str | None
    order: object | None
    position: Position | None
    message: str


class StockOptionsPaperRuntime:

    def __init__(
        self,
        execution_engine,
        portfolio_engine,
    ):
        self._execution_engine = execution_engine
        self._portfolio_engine = portfolio_engine
        self._risk_engine = StockOptionsRiskEngine()

        if not execution_engine.is_paper_engine():
            raise ValueError(
                "StockOptionsPaperRuntime requires a paper execution engine."
            )

    def execute(self, candidate_decision) -> StockOptionsPaperTradeResult:

        if candidate_decision is None:
            return StockOptionsPaperTradeResult(
                success=False,
                decision="NO_TRADE",
                symbol="",
                option_symbol=None,
                order=None,
                position=None,
                message="No candidate decision supplied.",
            )

        symbol = candidate_decision.symbol
        decision = candidate_decision.decision
        candidate = candidate_decision.candidate

        if decision != "CANDIDATE" or candidate is None:
            return StockOptionsPaperTradeResult(
                success=True,
                decision=decision,
                symbol=symbol,
                option_symbol=None,
                order=None,
                position=None,
                message="No paper trade executed because decision is not CANDIDATE.",
            )

        option_symbol = candidate.candidate.option_symbol
        lot_size = int(candidate.candidate.lot_size)
        option_price = float(candidate.quality.ltp)

        if not option_symbol:
            raise ValueError("Selected option symbol is empty.")

        if lot_size <= 0:
            raise ValueError(
                f"Invalid lot size for {option_symbol}: {lot_size}"
            )

        if option_price <= 0:
            raise ValueError(
                f"Invalid option price for {option_symbol}: {option_price}"
            )

        risk_result = self._risk_engine.evaluate(
            entry_price=option_price,
            quantity=lot_size,
        )

        if not risk_result.allowed:
            return StockOptionsPaperTradeResult(
                success=False,
                decision=decision,
                symbol=symbol,
                option_symbol=option_symbol,
                order=None,
                position=None,
                message=(
                    "Stock-option risk plan rejected: "
                    + "; ".join(risk_result.reasons)
                ),
            )

        order_request = OrderRequest(
            symbol=option_symbol,
            side=OrderSide.BUY,
            quantity=lot_size,
            price=option_price,
            strategy="STOCK_OPTIONS_PAPER_V1",
            metadata={
                "underlying_symbol": symbol,
                "direction": candidate_decision.direction,
                "option_type": candidate.candidate.option_type,
                "strike": candidate.candidate.strike,
                "expiry": candidate.candidate.expiry,
                "token": candidate.candidate.token,
                "exchange": candidate.candidate.exchange,
                "lot_size": lot_size,
                "quality_score": candidate.quality.quality_score,
                "quality_rank": candidate.quality.rank,
                "spread_percent": candidate.quality.spread_percent,
                "volume": candidate.quality.volume,
                "open_interest": candidate.quality.open_interest,
                "volume_oi_ratio": candidate.quality.volume_oi_ratio,
            },
        )

        order = self._execution_engine.submit_order(
            order_request
        )

        if not order.is_completed or order.filled_quantity != lot_size:
            return StockOptionsPaperTradeResult(
                success=False,
                decision=decision,
                symbol=symbol,
                option_symbol=option_symbol,
                order=order,
                position=None,
                message="Paper order was not completely filled.",
            )

        fill_price = float(
            order.average_price
            if order.average_price is not None
            else option_price
        )

        now = datetime.now(timezone.utc).isoformat()

        position = Position(
            symbol=option_symbol,
            quantity=order.filled_quantity,
            entry_price=fill_price,
            current_price=fill_price,
            stop_loss=risk_result.stop_loss,
            target_price=risk_result.target_price,
            opened_at=now,
            metadata={
                "underlying_symbol": symbol,
                "direction": candidate_decision.direction,
                "option_type": candidate.candidate.option_type,
                "strike": candidate.candidate.strike,
                "expiry": candidate.candidate.expiry,
                "token": candidate.candidate.token,
                "exchange": candidate.candidate.exchange,
                "lot_size": lot_size,
                "quality_score": candidate.quality.quality_score,
                "quality_rank": candidate.quality.rank,
                "risk_reward_ratio": risk_result.risk_reward_ratio,
                "risk_per_unit": risk_result.risk_per_unit,
                "maximum_loss": risk_result.maximum_loss,
                "maximum_reward": risk_result.maximum_reward,
                "risk_stop_loss": risk_result.stop_loss,
                "risk_target_price": risk_result.target_price,
                "paper_runtime": "STAGE_8A",
            },
        )

        self._portfolio_engine.open_position(position)

        return StockOptionsPaperTradeResult(
            success=True,
            decision=decision,
            symbol=symbol,
            option_symbol=option_symbol,
            order=order,
            position=position,
            message="Stock-option paper trade executed successfully.",
        )
