from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from tools.execution.order_models import OrderRequest, OrderSide
from tools.portfolio.portfolio_models import Position
from tools.risk.stock_options_risk_engine import StockOptionsRiskEngine


@dataclass(slots=True)
class SensexPaperTradeResult:
    success: bool
    decision: str
    symbol: str
    option_symbol: str | None
    order: object | None
    position: Position | None
    message: str


class SensexPaperRuntime:
    """
    Isolated SENSEX BFO option-buying runtime.

    HARD SAFETY:
        - SENSEX only
        - BFO only
        - PAPER execution engine only
        - no real broker execution path
    """

    MARKET = "SENSEX_FNO"
    UNDERLYING = "SENSEX"
    EXCHANGE = "BFO"

    # SENSEX BFO paper-trading configuration.
    # BFO SENSEX lot size is supplied by the instrument master.
    # Five lots are required for the paper-trading test bench.
    SENSEX_LOTS = 5

    def __init__(self, execution_engine, portfolio_engine) -> None:

        self._execution_engine = execution_engine
        self._portfolio_engine = portfolio_engine
        self._risk_engine = StockOptionsRiskEngine()

        if not execution_engine.is_paper_engine():
            raise ValueError(
                "SensexPaperRuntime requires a paper execution engine."
            )

    def execute(self, decision: dict) -> SensexPaperTradeResult:

        if not isinstance(decision, dict):

            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                self.UNDERLYING,
                None,
                None,
                None,
                "Invalid SENSEX decision.",
            )

        candidate = decision.get("candidate") or {}

        symbol = str(
            decision.get("symbol") or self.UNDERLYING
        ).upper()

        direction = str(
            decision.get("direction") or ""
        ).upper()

        if symbol != self.UNDERLYING:

            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                symbol,
                None,
                None,
                None,
                "SENSEX runtime accepts SENSEX only.",
            )

        if direction not in {"BULLISH", "BEARISH"}:

            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                symbol,
                None,
                None,
                None,
                "Invalid SENSEX direction.",
            )

        if (
            str(candidate.get("exchange") or "").upper()
            != self.EXCHANGE
        ):

            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                symbol,
                None,
                None,
                None,
                "SENSEX runtime accepts BFO contracts only.",
            )

        if (
            str(
                candidate.get(
                    "underlying",
                    self.UNDERLYING,
                )
                or self.UNDERLYING
            ).upper()
            != self.UNDERLYING
        ):

            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                symbol,
                None,
                None,
                None,
                "Candidate underlying must be SENSEX.",
            )

        option_symbol = str(
            candidate.get("option_symbol") or ""
        )

        option_type = str(
            candidate.get("option_type") or ""
        ).upper()

        contract_lot_size = int(
            candidate.get("lot_size") or 0
        )

        if contract_lot_size <= 0:
            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                symbol,
                option_symbol or None,
                None,
                None,
                "Invalid SENSEX contract lot size.",
            )

        # Always execute exactly SENSEX_LOTS lots.
        lot_size = (
            contract_lot_size
            * self.SENSEX_LOTS
        )

        option_price = float(
            decision.get("price") or 0
        )

        if (
            not option_symbol
            or option_type not in {"CE", "PE"}
            or lot_size <= 0
            or option_price <= 0
        ):

            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                symbol,
                option_symbol or None,
                None,
                None,
                "Invalid SENSEX option candidate.",
            )

        if (
            direction == "BULLISH"
            and option_type != "CE"
        ) or (
            direction == "BEARISH"
            and option_type != "PE"
        ):

            return SensexPaperTradeResult(
                False,
                "NO_TRADE",
                symbol,
                option_symbol,
                None,
                None,
                "SENSEX direction/option-type mismatch.",
            )

        risk = self._risk_engine.evaluate(
            entry_price=option_price,
            quantity=lot_size,
        )

        if not risk.allowed:

            return SensexPaperTradeResult(
                False,
                "CANDIDATE",
                symbol,
                option_symbol,
                None,
                None,
                "SENSEX risk plan rejected: "
                + "; ".join(risk.reasons),
            )

        order_request = OrderRequest(
            symbol=option_symbol,
            side=OrderSide.BUY,
            quantity=lot_size,
            price=option_price,
            strategy="SENSEX_PAPER_V1",
            metadata={
                "market": self.MARKET,
                "underlying_symbol": self.UNDERLYING,
                "direction": direction,
                "option_type": option_type,
                "strike": candidate.get("strike"),
                "expiry": candidate.get("expiry"),
                "token": candidate.get("token"),
                "exchange": self.EXCHANGE,
                "lot_size": lot_size,
                "paper_only": True,
            },
        )

        order = self._execution_engine.submit_order(
            order_request
        )

        if (
            not order.is_completed
            or order.filled_quantity != lot_size
        ):

            return SensexPaperTradeResult(
                False,
                "CANDIDATE",
                symbol,
                option_symbol,
                order,
                None,
                "SENSEX paper order was not completely filled.",
            )

        fill_price = float(
            order.average_price
            if order.average_price is not None
            else option_price
        )

        position = Position(
            symbol=option_symbol,
            quantity=order.filled_quantity,
            entry_price=fill_price,
            current_price=fill_price,
            stop_loss=risk.stop_loss,
            target_price=risk.target_price,
            opened_at=datetime.now(
                timezone.utc
            ).isoformat(),
            metadata={
                "market": self.MARKET,
                "underlying_symbol": self.UNDERLYING,
                "direction": direction,
                "option_type": option_type,
                "strike": candidate.get("strike"),
                "expiry": candidate.get("expiry"),
                "token": candidate.get("token"),
                "exchange": self.EXCHANGE,
                "contract_lot_size": contract_lot_size,
                "lots": self.SENSEX_LOTS,
                "quantity": lot_size,
                "lot_size": contract_lot_size,
                "risk_reward_ratio": risk.risk_reward_ratio,
                "risk_per_unit": risk.risk_per_unit,
                "maximum_loss": risk.maximum_loss,
                "maximum_reward": risk.maximum_reward,
                "paper_only": True,
            },
        )

        self._portfolio_engine.open_position(
            position
        )

        return SensexPaperTradeResult(
            True,
            "CANDIDATE",
            symbol,
            option_symbol,
            order,
            position,
            "SENSEX paper trade executed successfully.",
        )
