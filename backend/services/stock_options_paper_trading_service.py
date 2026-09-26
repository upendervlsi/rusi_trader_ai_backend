"""
RUSI Trader AI

Stock Options Paper Trading Service

Stage 9B

Isolated paper-trading service for the Stock Options module.

This service does NOT modify the existing NIFTY V1
paper-trading runtime.
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from core.broker_manager import BrokerManager

from tools.execution.paper_execution_engine import (
    PaperExecutionEngine,
)
from tools.execution.stock_options_paper_runtime import (
    StockOptionsPaperRuntime,
)
from tools.market_universe.stock_option_quality import (
    StockOptionQualityAnalyzer,
)
from tools.portfolio.portfolio_engine import (
    PortfolioEngine,
)
from tools.risk.stock_options_position_exit import (
    StockOptionsPositionExitService,
)
from tools.risk.stock_options_position_monitor import (
    StockOptionsPositionMonitor,
)
from tools.stock_options_observation.observation_runner import (
    StockOptionsObservationRunner,
)
from tools.portfolio.portfolio_models import Position


logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OBSERVATION_FILE = (
    PROJECT_ROOT
    / "runs"
    / "stock_options"
    / "observations.csv"
)

PAPER_STATE_FILE = (
    PROJECT_ROOT
    / "runs"
    / "stock_options"
    / "paper_state.json"
)

TRADE_HISTORY_FILE = (
    PROJECT_ROOT
    / "runs"
    / "stock_options"
    / "trade_history.json"
)


class StockOptionsPaperTradingService:

    INITIAL_CASH = 100000.0

    def __init__(self) -> None:

        self._execution_engine = (
            PaperExecutionEngine()
        )

        self._portfolio_engine = (
            PortfolioEngine(
                initial_cash=self.INITIAL_CASH,
            )
        )

        self._runtime = StockOptionsPaperRuntime(
            execution_engine=self._execution_engine,
            portfolio_engine=self._portfolio_engine,
        )

        self._broker_manager = BrokerManager()
        self._broker_initialized = False

        self._quality_analyzer = (
            StockOptionQualityAnalyzer()
        )

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
    # TRADE MAP HISTORY
    # ========================================================

    def _load_trade_history(self) -> None:

        if not TRADE_HISTORY_FILE.exists():
            self._trade_history = []
            return

        try:
            data = json.loads(
                TRADE_HISTORY_FILE.read_text()
            )

            if isinstance(data, list):
                self._trade_history = data
            else:
                self._trade_history = []

        except (
            OSError,
            json.JSONDecodeError,
        ):
            self._trade_history = []

    def _save_trade_history(self) -> None:

        TRADE_HISTORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_file = TRADE_HISTORY_FILE.with_suffix(
            ".json.tmp"
        )

        temp_file.write_text(
            json.dumps(
                self._trade_history,
                indent=2,
                default=str,
            )
        )

        temp_file.replace(
            TRADE_HISTORY_FILE
        )

    def _next_trade_number(self) -> int:

        numbers = []

        for event in self._trade_history:

            if not isinstance(event, dict):
                continue

            if str(
                event.get("event", "")
            ).upper() != "BUY":
                continue

            try:
                numbers.append(
                    int(
                        event.get(
                            "trade_number",
                            0,
                        )
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

        if not numbers:
            return 1

        return max(numbers) + 1

    def _current_trade_number(
        self,
        position: Position,
    ) -> int:

        for event in reversed(
            self._trade_history
        ):

            if not isinstance(event, dict):
                continue

            if str(
                event.get("event", "")
            ).upper() != "BUY":
                continue

            if event.get("symbol") != position.symbol:
                continue

            try:
                return int(
                    event.get(
                        "trade_number",
                        1,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                return 1

        return 1

    def _record_trade_event(
        self,
        *,
        event: str,
        position: Position,
        price: float,
        pnl: float | None = None,
        reason: str | None = None,
    ) -> None:

        event_name = str(event).upper()

        metadata = position.metadata or {}

        stored_trade_number = metadata.get(
            "trade_number"
        )

        if stored_trade_number is not None:
            try:
                trade_number = int(
                    stored_trade_number
                )
            except (
                TypeError,
                ValueError,
            ):
                trade_number = self._next_trade_number()
        elif event_name == "BUY":
            trade_number = self._next_trade_number()
        else:
            trade_number = self._current_trade_number(
                position
            )

        record = {
            "event": event_name,
            "trade_number": trade_number,
            "symbol": position.symbol,
            "timestamp": datetime.now(
                ).astimezone().isoformat(),
            "price": float(price),
            "quantity": int(
                position.quantity
            ),
        }

        if pnl is not None:
            record["pnl"] = float(pnl)

        if reason:
            record["reason"] = str(reason)

        record["option_type"] = metadata.get(
            "option_type"
        )

        record["direction"] = metadata.get(
            "direction"
        )

        record["underlying"] = (
            metadata.get("symbol")
        )

        self._trade_history.append(record)

        self._save_trade_history()

    def _record_price_observation(
        self,
        *,
        position: Position,
        price: float,
        pnl: float,
        peak_price: float,
        peak_pnl: float,
        protection_active: bool,
    ) -> None:

        metadata = position.metadata or {}

        trade_number = metadata.get(
            "trade_number"
        )

        if trade_number is None:
            trade_number = self._current_trade_number(
                position
            )

        record = {
            "event": "PRICE",
            "trade_number": int(trade_number),
            "symbol": position.symbol,
            "timestamp": datetime.now(
                ).astimezone().isoformat(),
            "price": float(price),
            "quantity": int(
                position.quantity
            ),
            "pnl": float(pnl),
            "peak_price": float(
                peak_price
            ),
            "peak_pnl": float(
                peak_pnl
            ),
            "protection_active": bool(
                protection_active
            ),
        }

        self._trade_history.append(record)

        self._save_trade_history()

    # ========================================================
    # PAPER STATE PERSISTENCE
    # ========================================================

    @staticmethod
    def _serialize_datetime(value) -> str | None:

        if value is None:
            return None

        if hasattr(value, "isoformat"):
            return value.isoformat()

        return str(value)

    def _position_to_dict(
        self,
        position: Position,
    ) -> dict:

        return {
            "symbol": position.symbol,
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "current_price": position.current_price,
            "stop_loss": position.stop_loss,
            "target_price": position.target_price,
            "opened_at": self._serialize_datetime(
                position.opened_at
            ),
            "metadata": position.metadata,
        }

    def _save_paper_state(self) -> None:

        state = {
            "version": 1,
            "mode": "PAPER",
            "initial_cash": self.INITIAL_CASH,
            "cash": self._portfolio_engine.state.cash,
            "realized_pnl": (
                self._portfolio_engine
                .state
                .realized_pnl
            ),
            "positions": {
                symbol: self._position_to_dict(position)
                for symbol, position in (
                    self._portfolio_engine
                    .state
                    .positions
                    .items()
                )
            },
        }

        PAPER_STATE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_file = PAPER_STATE_FILE.with_suffix(
            ".json.tmp"
        )

        temp_file.write_text(
            json.dumps(
                state,
                indent=2,
                default=str,
            )
        )

        temp_file.replace(
            PAPER_STATE_FILE
        )

    def _load_paper_state(self) -> None:

        if not PAPER_STATE_FILE.exists():
            return

        try:
            state = json.loads(
                PAPER_STATE_FILE.read_text()
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

            positions = state.get(
                "positions",
                {}
            )

            for symbol, data in positions.items():

                opened_at = data.get(
                    "opened_at"
                )

                if isinstance(opened_at, str):
                    try:
                        opened_at = datetime.fromisoformat(
                            opened_at
                        )
                    except ValueError:
                        pass

                position = Position(
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

                self._portfolio_engine.state.positions[
                    symbol
                ] = position

        except Exception as exc:

            print(
                "Stock Options paper-state restore failed: "
                f"{exc}"
            )

    # ========================================================
    # BROKER
    # ========================================================

    def _ensure_broker(self) -> None:

        if self._broker_initialized:
            return

        self._broker_manager.initialize()
        self._broker_initialized = True

    # ========================================================
    # OBSERVATION LOOKUP
    # ========================================================

    def _read_latest_candidates(
        self,
        symbols: list[str] | None = None,
        minimum_observed_at: datetime | None = None,
    ) -> dict[str, dict]:

        if not OBSERVATION_FILE.exists():
            return {}

        with OBSERVATION_FILE.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as fp:

            rows = list(
                csv.DictReader(fp)
            )

        latest: dict[str, dict] = {}

        allowed_symbols = None

        if symbols is not None:
            allowed_symbols = {
                str(symbol).strip().upper()
                for symbol in symbols
                if str(symbol).strip()
            }

        for row in rows:

            symbol = str(
                row.get("Symbol") or ""
            ).strip().upper()

            if not symbol:
                continue

            if (
                allowed_symbols is not None
                and symbol not in allowed_symbols
            ):
                continue

            if minimum_observed_at is not None:

                observed_at_raw = str(
                    row.get("ObservedAt") or ""
                ).strip()

                if not observed_at_raw:
                    continue

                try:
                    observed_at = datetime.fromisoformat(
                        observed_at_raw
                    )

                    if observed_at.tzinfo is None:
                        continue

                except ValueError:
                    continue

                if observed_at < minimum_observed_at:
                    continue

            if str(
                row.get("Decision") or ""
            ).strip().upper() != "CANDIDATE":
                continue

            option_symbol = str(
                row.get("OptionSymbol") or ""
            ).strip()

            if not option_symbol:
                continue

            latest[symbol] = row

        candidates = [
            row
            for row in latest.values()
            if str(row.get("Decision") or "").strip().upper()
            == "CANDIDATE"
        ]

        candidates.sort(
            key=lambda item: float(
                item.get("QualityScore") or 0
            ),
            reverse=True,
        )

        return {
            str(row.get("Symbol") or "").strip().upper(): row
            for row in candidates
            if str(row.get("Symbol") or "").strip()
        }

    # ========================================================
    # CANDIDATE
    # ========================================================

    def _find_candidate(
        self,
        option_symbol: str,
    ) -> dict | None:

        target = str(
            option_symbol or ""
        ).strip().upper()

        if not target:
            return None

        candidates = (
            self._read_latest_candidates()
        )

        for row in candidates.values():

            current = str(
                row.get("OptionSymbol") or ""
            ).strip().upper()

            if current == target:
                return row

        return None

    # ========================================================
    # FRESH QUOTE
    # ========================================================

    def _fresh_quote(
        self,
        candidate: dict,
    ) -> dict:

        self._ensure_broker()

        option_symbol = str(
            candidate.get("OptionSymbol") or ""
        ).strip()

        token = str(
            candidate.get("Token") or ""
        ).strip()

        exchange = str(
            candidate.get("Exchange") or "NFO"
        ).strip()

        if not option_symbol:
            raise ValueError(
                "Candidate option symbol is empty."
            )

        if not token:
            raise ValueError(
                f"Missing token for {option_symbol}."
            )

        response = (
            self._broker_manager
            .smartapi_client
            .get_quotes(
                exchange=exchange,
                symbol_tokens=[token],
            )
        )

        if not response:
            raise ValueError(
                f"Empty quote response for {option_symbol}."
            )

        return response

    # ========================================================
    # BUILD DECISION
    # ========================================================

    def _build_decision(
        self,
        candidate: dict,
        quote_response: dict,
    ):

        option_symbol = str(
            candidate.get("OptionSymbol") or ""
        ).strip()

        token = str(
            candidate.get("Token") or ""
        ).strip()

        exchange = str(
            candidate.get("Exchange") or "NFO"
        ).strip()

        option_type = str(
            candidate.get("OptionType") or ""
        ).strip().upper()

        symbol = str(
            candidate.get("Symbol") or ""
        ).strip().upper()

        direction = str(
            candidate.get("Direction") or ""
        ).strip().upper()

        analyzer_quality = (
            self._quality_analyzer.analyze(
                quote=quote_response,
                option_symbol=option_symbol,
                token=token,
            )
        )

        if analyzer_quality.ltp is None:
            raise ValueError(
                f"Fresh quote has no LTP for {option_symbol}."
            )

        lot_size = int(
            float(
                candidate.get("LotSize") or 0
            )
        )

        if lot_size <= 0:
            raise ValueError(
                f"Invalid lot size for {option_symbol}: "
                f"{lot_size}"
            )

        selected_candidate = SimpleNamespace(
            option_symbol=option_symbol,
            token=token,
            exchange=exchange,
            option_type=option_type,
            strike=float(
                candidate.get("Strike") or 0
            ),
            expiry=str(
                candidate.get("Expiry") or ""
            ),
            lot_size=lot_size,
            distance_percent=float(
                candidate.get("MetadataDistancePercent")
                or 0
            ),
        )

        quality = SimpleNamespace(
            option_symbol=option_symbol,
            token=token,
            ltp=analyzer_quality.ltp,
            mid_price=analyzer_quality.mid_price,
            spread=analyzer_quality.spread,
            spread_percent=analyzer_quality.spread_percent,
            volume=analyzer_quality.volume,
            open_interest=analyzer_quality.open_interest,
            volume_oi_ratio=analyzer_quality.volume_oi_ratio,
            bid_quantity=analyzer_quality.bid_quantity,
            ask_quantity=analyzer_quality.ask_quantity,
            depth_quantity=analyzer_quality.depth_quantity,
            depth_imbalance=analyzer_quality.depth_imbalance,
            quote_completeness=analyzer_quality.quote_completeness,
            quality_score=float(
                candidate.get("QualityScore") or 0
            ),
            rank=int(
                float(
                    candidate.get("QualityRank") or 0
                )
            ),
            components=analyzer_quality.components,
        )

        selected = SimpleNamespace(
            candidate=selected_candidate,
            quality=quality,
        )

        return SimpleNamespace(
            symbol=symbol,
            decision="CANDIDATE",
            direction=direction,
            underlying_price=float(
                candidate.get("UnderlyingPrice") or 0
            ),
            bullish_score=float(
                candidate.get("BullishScore") or 0
            ),
            bearish_score=float(
                candidate.get("BearishScore") or 0
            ),
            analysis_reason=str(
                candidate.get("AnalysisReason") or ""
            ),
            candidate=selected,
            metadata={
                "source": "stock_options_observation",
                "fresh_quote": True,
            },
        )

    # ========================================================
    # PAPER TRADE
    # ========================================================

    def paper_trade(
        self,
        option_symbol: str,
    ) -> dict:

        candidate = self._find_candidate(
            option_symbol
        )

        if candidate is None:
            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    "Selected option is not a current "
                    "eligible Stock Options candidate."
                ),
            }

        quote_response = self._fresh_quote(
            candidate
        )

        decision = self._build_decision(
            candidate=candidate,
            quote_response=quote_response,
        )

        result = self._runtime.execute(
            decision
        )

        position = result.position

        if result.success and position is not None:

            trade_number = self._next_trade_number()

            if position.metadata is None:
                position.metadata = {}

            position.metadata["trade_number"] = (
                trade_number
            )

            self._record_trade_event(
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
            "order": (
                {
                    "order_id": result.order.order_id,
                    "status": result.order.status.value,
                    "filled_quantity": result.order.filled_quantity,
                    "average_price": result.order.average_price,
                }
                if result.order is not None
                else None
            ),
            "position": (
                {
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "entry_price": position.entry_price,
                    "current_price": position.current_price,
                    "stop_loss": position.stop_loss,
                    "target_price": position.target_price,
                    "opened_at": position.opened_at,
                    "metadata": position.metadata,
                }
                if position is not None
                else None
            ),
        }

    # ========================================================
    # TOP CANDIDATE PAPER TRADE
    # ========================================================

    def paper_trade_top(
        self,
        symbols: list[str] | None = None,
        minimum_observed_at: datetime | None = None,
    ) -> dict:
        """
        Attempt the highest-quality current Stock Options
        candidate first.

        Candidates are already ordered by QualityScore.
        Each candidate receives a fresh quote and fresh risk
        validation before paper execution.

        A risk-rejected candidate is skipped and the next
        quality-ranked candidate is evaluated.

        No real broker order is submitted.
        """

        candidates = list(
            self._read_latest_candidates(
                symbols=symbols,
                minimum_observed_at=minimum_observed_at,
            ).values()
        )

        if not candidates:
            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    "No current Stock Options candidates available."
                ),
                "evaluated_candidates": 0,
            }

        existing_positions = list(
            self._portfolio_engine
            .state
            .positions
            .values()
        )

        if existing_positions:
            position = existing_positions[0]

            return {
                "success": False,
                "decision": "NO_TRADE",
                "message": (
                    "A Stock Options paper position is already open."
                ),
                "evaluated_candidates": 0,
                "position": {
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "entry_price": position.entry_price,
                    "current_price": position.current_price,
                    "stop_loss": position.stop_loss,
                    "target_price": position.target_price,
                    "opened_at": position.opened_at,
                    "metadata": position.metadata,
                },
            }

        evaluated = []

        for row in candidates:

            option_symbol = str(
                row.get("OptionSymbol") or ""
            ).strip()

            if not option_symbol:
                continue

            try:
                quote_response = self._fresh_quote(
                    row
                )

                decision = self._build_decision(
                    candidate=row,
                    quote_response=quote_response,
                )

                candidate = decision.candidate.candidate
                quality = decision.candidate.quality

                risk = self._runtime._risk_engine.evaluate(
                    entry_price=quality.ltp,
                    quantity=candidate.lot_size,
                )

                evaluated.append(
                    {
                        "symbol": row.get("Symbol"),
                        "option_symbol": option_symbol,
                        "direction": row.get("Direction"),
                        "quality_score": float(
                            row.get("QualityScore") or 0
                        ),
                        "fresh_ltp": quality.ltp,
                        "risk_allowed": risk.allowed,
                        "risk_reward_ratio": (
                            risk.risk_reward_ratio
                        ),
                        "reason": list(
                            risk.reasons
                        ),
                    }
                )

                if not risk.allowed:
                    continue

                result = self._runtime.execute(
                    decision
                )

                if (
                    result.success
                    and result.position is not None
                ):
                    trade_number = (
                        self._next_trade_number()
                    )

                    if result.position.metadata is None:
                        result.position.metadata = {}

                    result.position.metadata[
                        "trade_number"
                    ] = trade_number

                    self._record_trade_event(
                        event="BUY",
                        position=result.position,
                        price=result.position.entry_price,
                    )

                    self._save_paper_state()

                return {
                    "success": result.success,
                    "decision": result.decision,
                    "symbol": result.symbol,
                    "option_symbol": result.option_symbol,
                    "message": result.message,
                    "evaluated_candidates": len(
                        evaluated
                    ),
                    "risk": {
                        "allowed": risk.allowed,
                        "stop_loss": risk.stop_loss,
                        "target_price": risk.target_price,
                        "risk_reward_ratio": (
                            risk.risk_reward_ratio
                        ),
                        "maximum_loss": (
                            risk.maximum_loss
                        ),
                        "maximum_reward": (
                            risk.maximum_reward
                        ),
                        "reasons": risk.reasons,
                    },
                    "evaluated": evaluated,
                    "order": (
                        {
                            "order_id": result.order.order_id,
                            "status": result.order.status.value,
                            "filled_quantity": (
                                result.order.filled_quantity
                            ),
                            "average_price": (
                                result.order.average_price
                            ),
                        }
                        if result.order is not None
                        else None
                    ),
                    "position": (
                        {
                            "symbol": result.position.symbol,
                            "quantity": result.position.quantity,
                            "entry_price": (
                                result.position.entry_price
                            ),
                            "current_price": (
                                result.position.current_price
                            ),
                            "stop_loss": (
                                result.position.stop_loss
                            ),
                            "target_price": (
                                result.position.target_price
                            ),
                            "opened_at": (
                                result.position.opened_at
                            ),
                            "metadata": (
                                result.position.metadata
                            ),
                        }
                        if result.position is not None
                        else None
                    ),
                }

            except Exception as exc:
                evaluated.append(
                    {
                        "symbol": row.get("Symbol"),
                        "option_symbol": option_symbol,
                        "direction": row.get("Direction"),
                        "quality_score": float(
                            row.get("QualityScore") or 0
                        ),
                        "risk_allowed": False,
                        "error": str(exc),
                    }
                )

        return {
            "success": False,
            "decision": "NO_TRADE",
            "message": (
                "No quality-ranked Stock Options candidate "
                "passed fresh quote and risk validation."
            ),
            "evaluated_candidates": len(evaluated),
            "evaluated": evaluated,
        }

    # ========================================================
    # FRESH POSITION INTELLIGENCE
    # ========================================================

    def _refresh_position_intelligence(
        self,
        position,
    ) -> dict:
        """
        Refresh Stock Options intelligence for the currently
        open position only.

        This intentionally scans only the underlying symbol of
        the open option. It does not run the complete Stock
        Options universe scan and does not place orders.

        Returns:
            {
                "available": bool,
                "direction": str | None,
                "confidence": float,
                "bullish_score": float,
                "bearish_score": float,
                "decision": str,
                "reason": str,
                "symbol": str | None,
            }
        """

        metadata = (
            getattr(position, "metadata", None)
            or {}
        )

        underlying_symbol = (
            metadata.get("underlying_symbol")
            or metadata.get("symbol")
        )

        if not underlying_symbol:
            return {
                "available": False,
                "direction": None,
                "confidence": 0.0,
                "bullish_score": 0.0,
                "bearish_score": 0.0,
                "decision": "",
                "reason": "Underlying symbol unavailable.",
                "symbol": None,
            }

        underlying_symbol = (
            str(underlying_symbol)
            .strip()
            .upper()
        )

        try:
            runner = StockOptionsObservationRunner(
                history_days=7,
                interval="FIVE_MINUTE",
                market_request_delay_seconds=3.0,
                option_request_delay_seconds=0.0,
            )

            refresh_result = runner.run(
                symbols=[underlying_symbol]
            )

            if not refresh_result.success:
                logger.warning(
                    "Stock Options position intelligence "
                    "refresh failed | symbol=%s | errors=%s",
                    underlying_symbol,
                    refresh_result.errors,
                )

                return {
                    "available": False,
                    "direction": None,
                    "confidence": 0.0,
                    "bullish_score": 0.0,
                    "bearish_score": 0.0,
                    "decision": "",
                    "reason": "Fresh observation refresh failed.",
                    "symbol": underlying_symbol,
                }

            if not OBSERVATION_FILE.exists():
                return {
                    "available": False,
                    "direction": None,
                    "confidence": 0.0,
                    "bullish_score": 0.0,
                    "bearish_score": 0.0,
                    "decision": "",
                    "reason": "Observation file unavailable.",
                    "symbol": underlying_symbol,
                }

            latest = None

            with OBSERVATION_FILE.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as handle:

                reader = csv.DictReader(handle)

                for row in reader:
                    row_symbol = str(
                        row.get("Symbol", "")
                    ).strip().upper()

                    if row_symbol == underlying_symbol:
                        latest = row

            if latest is None:
                return {
                    "available": False,
                    "direction": None,
                    "confidence": 0.0,
                    "bullish_score": 0.0,
                    "bearish_score": 0.0,
                    "decision": "",
                    "reason": (
                        "No fresh observation found for "
                        f"{underlying_symbol}."
                    ),
                    "symbol": underlying_symbol,
                }

            direction = str(
                latest.get("Direction", "")
            ).strip().upper()

            decision = str(
                latest.get("Decision", "")
            ).strip().upper()

            try:
                bullish_score = float(
                    latest.get(
                        "BullishScore",
                        0.0,
                    )
                    or 0.0
                )
            except (TypeError, ValueError):
                bullish_score = 0.0

            try:
                bearish_score = float(
                    latest.get(
                        "BearishScore",
                        0.0,
                    )
                    or 0.0
                )
            except (TypeError, ValueError):
                bearish_score = 0.0

            #
            # Confidence must represent the strength of the
            # CURRENT direction. This is important for reversal
            # detection.
            #
            if direction == "BULLISH":
                confidence = bullish_score
            elif direction == "BEARISH":
                confidence = bearish_score
            else:
                confidence = 0.0

            reason = str(
                latest.get(
                    "AnalysisReason",
                    "",
                )
                or ""
            )

            logger.info(
                "Stock Options Position Intelligence | "
                "underlying=%s direction=%s confidence=%.4f "
                "bullish=%.4f bearish=%.4f decision=%s",
                underlying_symbol,
                direction,
                confidence,
                bullish_score,
                bearish_score,
                decision,
            )

            return {
                "available": (
                    direction in {
                        "BULLISH",
                        "BEARISH",
                    }
                ),
                "direction": direction or None,
                "confidence": confidence,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score,
                "decision": decision,
                "reason": reason,
                "symbol": underlying_symbol,
            }

        except Exception as exc:

            logger.exception(
                "Stock Options position intelligence "
                "exception | symbol=%s",
                underlying_symbol,
            )

            return {
                "available": False,
                "direction": None,
                "confidence": 0.0,
                "bullish_score": 0.0,
                "bearish_score": 0.0,
                "decision": "",
                "reason": str(exc),
                "symbol": underlying_symbol,
            }


    # ========================================================
    # POSITION MONITORING
    # ========================================================

    def monitor_open_position(self) -> dict:
        """
        Monitor the currently open Stock Options paper position.

        Uses a fresh option quote and the existing
        StockOptionsPositionMonitor. If the monitor requests
        EXIT, the existing StockOptionsPositionExitService
        closes the position through the same PortfolioEngine.

        No new position is opened by this method.
        """

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
                "message": (
                    "No Stock Options paper position is open."
                ),
                "position": None,
            }

        position = positions[0]

        metadata = position.metadata or {}

        token = str(
            metadata.get("token") or ""
        ).strip()

        exchange = str(
            metadata.get("exchange") or "NFO"
        ).strip()

        if not token:
            return {
                "success": False,
                "action": "HOLD",
                "message": (
                    "Open position is missing its broker token."
                ),
                "position": {
                    "symbol": position.symbol,
                },
            }

        self._ensure_broker()

        quote_response = (
            self._broker_manager
            .smartapi_client
            .get_quotes(
                exchange=exchange,
                symbol_tokens=[token],
            )
        )

        if not quote_response:
            return {
                "success": False,
                "action": "HOLD",
                "message": (
                    f"Empty quote response for {position.symbol}."
                ),
                "position": {
                    "symbol": position.symbol,
                },
            }

        quote = None

        if isinstance(quote_response, dict):

            data = quote_response.get(
                "data"
            )

            if isinstance(data, list) and data:
                quote = data[0]

            elif isinstance(data, dict):
                fetched = data.get("fetched")

                if isinstance(fetched, list) and fetched:
                    quote = fetched[0]

                elif isinstance(fetched, dict):
                    quote = fetched

                elif "ltp" in data:
                    quote = data

            elif "ltp" in quote_response:
                quote = quote_response

        if not isinstance(quote, dict):
            return {
                "success": False,
                "action": "HOLD",
                "message": (
                    f"Unable to parse quote for {position.symbol}."
                ),
                "position": {
                    "symbol": position.symbol,
                },
            }

        raw_ltp = (
            quote.get("ltp")
            if quote.get("ltp") is not None
            else quote.get("lastTradedPrice")
        )

        if raw_ltp is None:
            return {
                "success": False,
                "action": "HOLD",
                "message": (
                    f"Quote has no LTP for {position.symbol}."
                ),
                "position": {
                    "symbol": position.symbol,
                },
            }

        current_price = float(raw_ltp)

        if current_price <= 0:
            return {
                "success": False,
                "action": "HOLD",
                "message": (
                    f"Invalid LTP for {position.symbol}: "
                    f"{current_price}"
                ),
                "position": {
                    "symbol": position.symbol,
                },
            }

        #
        # Fresh Stock Options intelligence for the currently
        # open position.
        #
        # Only the underlying of this position is refreshed.
        # No full-universe scan is performed here.
        #
        position_intelligence = (
            self._refresh_position_intelligence(
                position
            )
        )

        market_direction = (
            position_intelligence.get(
                "direction"
            )
            if position_intelligence.get(
                "available",
                False,
            )
            else None
        )

        market_confidence = float(
            position_intelligence.get(
                "confidence",
                0.0,
            )
            or 0.0
        )

        logger.info(
            "Stock Options Position Monitor Input | "
            "option=%s direction=%s confidence=%.4f",
            position.symbol,
            market_direction,
            market_confidence,
        )

        monitor_result = (
            self._position_monitor.monitor(
                position=position,
                current_price=current_price,
                market_direction=market_direction,
                market_confidence=market_confidence,
            )
        )

        exit_result = (
            self._position_exit.apply(
                position=position,
                monitor_result=monitor_result,
            )
        )

        # Record the actual monitored price before returning.
        self._record_price_observation(
            position=position,
            price=current_price,
            pnl=monitor_result.unrealized_pnl,
            peak_price=monitor_result.peak_price,
            peak_pnl=monitor_result.peak_pnl,
            protection_active=(
                monitor_result.profit_protection_active
            ),
        )

        # Record automatic exits separately from price observations.
        if (
            monitor_result.action == "EXIT"
            and exit_result.success
        ):
            self._record_trade_event(
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
            "message": exit_result.message,
            "symbol": position.symbol,
            "current_price": monitor_result.current_price,
            "unrealized_pnl": monitor_result.unrealized_pnl,
            "peak_price": monitor_result.peak_price,
            "peak_pnl": monitor_result.peak_pnl,
            "protected_price": monitor_result.protected_price,
            "profit_protection_active": (
                monitor_result.profit_protection_active
            ),
            "reversal_count": (
                monitor_result.reversal_count
            ),
            "position_intelligence": (
                position_intelligence
            ),
            "realized_pnl": exit_result.realized_pnl,
            "position": (
                {
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "entry_price": position.entry_price,
                    "current_price": position.current_price,
                    "stop_loss": position.stop_loss,
                    "target_price": position.target_price,
                    "opened_at": position.opened_at,
                    "metadata": position.metadata,
                }
                if position.symbol
                in self._portfolio_engine.state.positions
                else None
            ),
        }

    # ========================================================
    # STATUS
    # ========================================================

    def close_paper_position_admin(self) -> dict:
        """
        Administrative PAPER-only close.

        This closes the existing Stock Options paper position
        through PortfolioEngine only.

        No real broker order is submitted.
        Normal monitor/exit logic is unchanged.
        """

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
                "message": (
                    "No Stock Options paper position is open."
                ),
                "position": None,
            }

        position = positions[0]

        closed_position = (
            self._portfolio_engine.close_position(
                position.symbol
            )
        )

        self._record_trade_event(
            event="EXIT",
            position=closed_position,
            price=closed_position.current_price,
            pnl=closed_position.unrealized_pnl,
            reason="ADMIN_CLOSE",
        )

        self._save_paper_state()

        return {
            "success": True,
            "action": "ADMIN_CLOSE",
            "symbol": closed_position.symbol,
            "entry_price": closed_position.entry_price,
            "close_price": closed_position.current_price,
            "quantity": closed_position.quantity,
            "realized_pnl": float(
                closed_position.unrealized_pnl
            ),
            "message": (
                "Stock Options paper position "
                "administratively closed."
            ),
        }

    def status(self) -> dict:

        summary = (
            self._portfolio_engine
            .portfolio_summary()
        )

        positions = []

        for position in (
            self._portfolio_engine
            .state
            .positions
            .values()
        ):

            positions.append(
                {
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "entry_price": position.entry_price,
                    "current_price": position.current_price,
                    "stop_loss": position.stop_loss,
                    "target_price": position.target_price,
                    "opened_at": position.opened_at,
                    "metadata": position.metadata,
                }
            )

        return {
            "mode": "PAPER",
            "available_cash": summary.available_cash,
            "invested_capital": summary.invested_capital,
            "total_market_value": summary.total_market_value,
            "unrealized_pnl": summary.unrealized_pnl,
            "realized_pnl": summary.realized_pnl,
            "open_positions": summary.open_positions,
            "positions": positions,
        }
