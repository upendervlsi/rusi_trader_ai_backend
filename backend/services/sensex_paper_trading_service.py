from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from core.broker_manager import BrokerManager

from tools.execution.paper_execution_engine import (
    PaperExecutionEngine,
)

from tools.execution.sensex_paper_runtime import (
    SensexPaperRuntime,
)

from tools.portfolio.portfolio_engine import (
    PortfolioEngine,
)

from tools.portfolio.portfolio_models import (
    Position,
)

from tools.risk.stock_options_position_exit import (
    StockOptionsPositionExitService,
)

from tools.risk.stock_options_position_monitor import (
    StockOptionsPositionMonitor,
)


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

STATE_DIR = (
    PROJECT_ROOT
    / "runs"
    / "sensex_fno"
)

PAPER_STATE_FILE = (
    STATE_DIR
    / "paper_state.json"
)

TRADE_HISTORY_FILE = (
    STATE_DIR
    / "trade_history.json"
)


class SensexPaperTradingService:

    INITIAL_CASH = 100000.0

    MARKET = "SENSEX_FNO"
    UNDERLYING = "SENSEX"
    EXCHANGE = "BFO"

    SENSEX_LOTS = 5
    SENSEX_CONTRACT_LOT_SIZE = 20
    SENSEX_QUANTITY = (
        SENSEX_LOTS * SENSEX_CONTRACT_LOT_SIZE
    )

    def __init__(self) -> None:

        self._execution_engine = (
            PaperExecutionEngine()
        )

        if not self._execution_engine.is_paper_engine():

            raise RuntimeError(
                "SENSEX PAPER runtime requires "
                "PaperExecutionEngine."
            )

        self._portfolio_engine = (
            PortfolioEngine(
                initial_cash=self.INITIAL_CASH
            )
        )

        self._runtime = (
            SensexPaperRuntime(
                execution_engine=self._execution_engine,
                portfolio_engine=self._portfolio_engine,
            )
        )

        self._broker_manager = BrokerManager()
        self._broker_initialized = False

        self._position_monitor = (
            StockOptionsPositionMonitor()
        )

        self._position_exit = (
            StockOptionsPositionExitService(
                self._portfolio_engine
            )
        )

        self._trade_history = []

        self._load_trade_history()
        self._load_paper_state()

    # ========================================================
    # BROKER QUOTES
    # ========================================================

    def _ensure_broker(self) -> None:

        if self._broker_initialized:
            return

        self._broker_manager.initialize()
        self._broker_initialized = True

    @staticmethod
    def _extract_quote(response):

        if not isinstance(response, dict):
            return None

        data = response.get("data")

        if isinstance(data, list) and data:
            return data[0]

        if isinstance(data, dict):

            fetched = data.get("fetched")

            if isinstance(fetched, list) and fetched:
                return fetched[0]

            if isinstance(fetched, dict):
                return fetched

            if "ltp" in data:
                return data

        if "ltp" in response:
            return response

        return None

    def quote(
        self,
        token: str,
        exchange: str = EXCHANGE,
    ) -> dict:

        if exchange.upper() != self.EXCHANGE:
            raise ValueError(
                "SENSEX quote path accepts BFO only."
            )

        self._ensure_broker()

        response = (
            self._broker_manager
            .smartapi_client
            .get_quotes(
                exchange=self.EXCHANGE,
                symbol_tokens=[str(token)],
            )
        )

        quote = self._extract_quote(response)

        if not quote:
            raise RuntimeError(
                f"No quote returned for "
                f"{self.EXCHANGE}:{token}"
            )

        raw_ltp = quote.get(
            "ltp",
            quote.get("lastTradedPrice"),
        )

        price = float(raw_ltp or 0)

        if price <= 0:
            raise RuntimeError(
                f"Invalid LTP for "
                f"{self.EXCHANGE}:{token}: {price}"
            )

        return quote

    # ========================================================
    # PAPER ENTRY
    # ========================================================

    def paper_trade(
        self,
        candidate: dict,
        direction: str,
    ) -> dict:

        direction = str(
            direction
        ).upper().strip()

        if direction not in {
            "BULLISH",
            "BEARISH",
        }:

            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    "Direction must be "
                    "BULLISH or BEARISH."
                ),
            }

        required = (
            "option_symbol",
            "token",
            "exchange",
            "option_type",
            "strike",
            "expiry",
            "lot_size",
        )

        missing = [
            key
            for key in required
            if candidate.get(key)
            in (None, "")
        ]

        if missing:

            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    f"Missing candidate fields: "
                    f"{missing}"
                ),
            }

        if (
            str(candidate["exchange"])
            .upper()
            != self.EXCHANGE
        ):

            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    "SENSEX paper execution "
                    "accepts BFO contracts only."
                ),
            }

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

            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    "Candidate underlying "
                    "must be SENSEX."
                ),
            }

        if self._portfolio_engine.state.positions:

            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    "SENSEX paper position "
                    "already open."
                ),
            }

        quote = self.quote(
            token=str(candidate["token"]),
            exchange=self.EXCHANGE,
        )

        price = float(
            quote.get(
                "ltp",
                quote.get(
                    "lastTradedPrice",
                    0,
                ),
            )
            or 0
        )

        decision = {
            "symbol": self.UNDERLYING,
            "direction": direction,
            "candidate": candidate,
            "price": price,
        }

        result = self._runtime.execute(
            decision
        )

        position = result.position

        if result.success and position:

            self._record(
                event="BUY",
                position=position,
                price=position.entry_price,
            )

            self._save_paper_state()

        return {
            "success": result.success,
            "decision": result.decision,
            "symbol": result.symbol,
            "option_symbol": result.option_symbol,
            "message": result.message,
            "position": (
                self._position_dict(position)
                if position
                else None
            ),
        }

    # ========================================================
    # POSITION MONITOR
    # ========================================================

    def monitor_open_position(self) -> dict:

        positions = list(
            self._portfolio_engine
            .state
            .positions
            .values()
        )

        if not positions:

            return {
                "success": True,
                "action": "NO_POSITION",
                "position": None,
            }

        position = positions[0]

        metadata = (
            position.metadata or {}
        )

        token = str(
            metadata.get("token") or ""
        ).strip()

        if not token:

            return {
                "success": False,
                "action": "HOLD",
                "message": (
                    "Open SENSEX position "
                    "has no broker token."
                ),
            }

        quote = self.quote(
            token=token,
            exchange=self.EXCHANGE,
        )

        current_price = float(
            quote.get(
                "ltp",
                quote.get(
                    "lastTradedPrice",
                    0,
                ),
            )
            or 0
        )

        if current_price <= 0:

            return {
                "success": False,
                "action": "HOLD",
                "message": (
                    "Invalid SENSEX "
                    "option LTP."
                ),
            }

        direction = str(
            metadata.get("direction") or ""
        )

        monitor_result = (
            self._position_monitor.monitor(
                position=position,
                current_price=current_price,
                market_direction=(
                    direction
                    if direction
                    in {
                        "BULLISH",
                        "BEARISH",
                    }
                    else None
                ),
                market_confidence=1.0,
            )
        )

        exit_result = (
            self._position_exit.apply(
                position=position,
                monitor_result=monitor_result,
            )
        )

        if (
            monitor_result.action == "EXIT"
            and exit_result.success
        ):

            self._record(
                event="EXIT",
                position=position,
                price=current_price,
                pnl=exit_result.realized_pnl,
                reason=monitor_result.reason,
            )

        self._save_paper_state()

        return {
            "success": exit_result.success,
            "action": monitor_result.action,
            "reason": monitor_result.reason,
            "current_price": current_price,
            "unrealized_pnl": monitor_result.unrealized_pnl,
            "peak_price": monitor_result.peak_price,
            "peak_pnl": monitor_result.peak_pnl,
            "protected_price": monitor_result.protected_price,
            "profit_protection_active": (
                monitor_result.profit_protection_active
            ),
            "realized_pnl": exit_result.realized_pnl,
            "position": (
                self._position_dict(position)
                if position.symbol
                in self._portfolio_engine.state.positions
                else None
            ),
        }

    # ========================================================
    # ADMIN PAPER CLOSE
    # ========================================================

    def close_paper_position_admin(
        self,
        reason: str = "ADMIN_CLOSE",
    ) -> dict:

        positions = list(
            self._portfolio_engine
            .state
            .positions
            .values()
        )

        if not positions:

            return {
                "success": True,
                "action": "NO_POSITION",
                "position": None,
            }

        position = positions[0]

        closed = (
            self._portfolio_engine
            .close_position(
                position.symbol
            )
        )

        self._record(
            event="EXIT",
            position=closed,
            price=closed.current_price,
            pnl=closed.unrealized_pnl,
            reason=reason,
        )

        self._save_paper_state()

        return {
            "success": True,
            "action": reason,
            "symbol": closed.symbol,
            "entry_price": closed.entry_price,
            "close_price": closed.current_price,
            "quantity": closed.quantity,
            "realized_pnl": float(
                closed.unrealized_pnl
            ),
        }

    # ========================================================
    # STATUS
    # ========================================================

    def status(self) -> dict:

        summary = (
            self._portfolio_engine
            .portfolio_summary()
        )

        return {
            "success": True,
            "mode": "PAPER",
            "market": self.MARKET,
            "exchange": self.EXCHANGE,
            "underlying": self.UNDERLYING,
            "initial_cash": self.INITIAL_CASH,
            "summary": summary,
            "open_positions": len(
                self._portfolio_engine
                .state
                .positions
            ),
            "positions": [
                self._position_dict(position)
                for position in (
                    self._portfolio_engine
                    .state
                    .positions
                    .values()
                )
            ],
            "trade_count": sum(
                1
                for event in self._trade_history
                if event.get("event") == "BUY"
            ),
            "realized_pnl": float(
                self._portfolio_engine
                .state
                .realized_pnl
            ),
        }

    # ========================================================
    # PERSISTENCE
    # ========================================================

    @staticmethod
    def _position_dict(
        position: Position | None,
    ) -> dict | None:

        if position is None:
            return None

        return {
            "symbol": position.symbol,
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "current_price": position.current_price,
            "stop_loss": position.stop_loss,
            "target_price": position.target_price,
            "opened_at": position.opened_at,
            "metadata": position.metadata,
        }

    def _record(
        self,
        event: str,
        position: Position,
        price: float,
        pnl: float | None = None,
        reason: str | None = None,
    ) -> None:

        metadata = (
            position.metadata or {}
        )

        record = {
            "event": event,
            "trade_number": (
                1
                + sum(
                    1
                    for item
                    in self._trade_history
                    if item.get("event")
                    == "BUY"
                )
            ),
            "symbol": position.symbol,
            "timestamp": (
                datetime.now()
                .astimezone()
                .isoformat()
            ),
            "price": float(price),
            "quantity": int(
                position.quantity
            ),
            "underlying": self.UNDERLYING,
            "option_type": metadata.get(
                "option_type"
            ),
            "direction": metadata.get(
                "direction"
            ),
        }

        if pnl is not None:
            record["pnl"] = float(pnl)

        if reason:
            record["reason"] = reason

        self._trade_history.append(
            record
        )

        self._save_trade_history()

    def _save_trade_history(self) -> None:

        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp = (
            TRADE_HISTORY_FILE
            .with_suffix(".json.tmp")
        )

        tmp.write_text(
            json.dumps(
                self._trade_history,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        tmp.replace(
            TRADE_HISTORY_FILE
        )

    def _save_paper_state(self) -> None:

        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        state = {
            "version": 1,
            "mode": "PAPER",
            "market": self.MARKET,
            "exchange": self.EXCHANGE,
            "underlying": self.UNDERLYING,
            "initial_cash": self.INITIAL_CASH,
            "cash": (
                self._portfolio_engine
                .state
                .cash
            ),
            "realized_pnl": (
                self._portfolio_engine
                .state
                .realized_pnl
            ),
            "positions": {
                symbol: self._position_dict(
                    position
                )
                for symbol, position in (
                    self._portfolio_engine
                    .state
                    .positions
                    .items()
                )
            },
        }

        tmp = (
            PAPER_STATE_FILE
            .with_suffix(".json.tmp")
        )

        tmp.write_text(
            json.dumps(
                state,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        tmp.replace(
            PAPER_STATE_FILE
        )

    def _load_trade_history(self) -> None:

        if not TRADE_HISTORY_FILE.exists():
            self._trade_history = []
            return

        try:

            data = json.loads(
                TRADE_HISTORY_FILE.read_text(
                    encoding="utf-8"
                )
            )

            self._trade_history = (
                data
                if isinstance(data, list)
                else []
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):

            self._trade_history = []

    def _load_paper_state(self) -> None:

        if not PAPER_STATE_FILE.exists():
            return

        try:

            state = json.loads(
                PAPER_STATE_FILE.read_text(
                    encoding="utf-8"
                )
            )

            self._portfolio_engine.state.cash = float(
                state.get(
                    "cash",
                    self.INITIAL_CASH,
                )
            )

            self._portfolio_engine.state.realized_pnl = float(
                state.get(
                    "realized_pnl",
                    0.0,
                )
            )

            for (
                symbol,
                data,
            ) in (
                state.get("positions")
                or {}
            ).items():

                opened_at = data.get(
                    "opened_at"
                )

                if isinstance(
                    opened_at,
                    str,
                ):

                    try:
                        opened_at = (
                            datetime.fromisoformat(
                                opened_at
                            )
                        )
                    except ValueError:
                        pass

                self._portfolio_engine.state.positions[
                    symbol
                ] = Position(
                    symbol=data["symbol"],
                    quantity=float(
                        data["quantity"]
                    ),
                    entry_price=float(
                        data["entry_price"]
                    ),
                    current_price=float(
                        data["current_price"]
                    ),
                    stop_loss=float(
                        data["stop_loss"]
                    ),
                    target_price=float(
                        data["target_price"]
                    ),
                    opened_at=opened_at,
                    metadata=data.get(
                        "metadata",
                        {},
                    ),
                )

        except Exception:

            logger.exception(
                "Failed to restore "
                "SENSEX paper state."
            )
