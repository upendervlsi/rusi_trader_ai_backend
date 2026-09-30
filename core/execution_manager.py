"""
============================================================

Execution Manager

============================================================
"""

from datetime import datetime, UTC, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

from common.logger import get_logger
from common.enums import ExecutionMode

from core.broker_manager import BrokerManager
from providers.angel.nifty_real_order_executor import (
    NiftyRealOrderExecutor,
)
from core.nifty_real_pending_order import (
    NiftyRealPendingOrder,
)
from core.nifty_real_pending_exit_order import (
    NiftyRealPendingExitOrder,
)
from core.nifty_real_exit_monitor import (
    NiftyRealExitMonitor,
)
from core.nifty_real_pnl_store import (
    NiftyRealPnlStore,
)
from core.nifty_real_trading_control import (
    NiftyRealTradingControl,
)
from builders.candle_builder import CandleBuilder
from builders.market_snapshot_builder import MarketSnapshotBuilder
from intelligence.intelligence_manager import IntelligenceManager
from intelligence.features.feature_engine import FeatureEngine

from intelligence.features.default_feature_registry import (
    create_default_feature_registry,
)

from intelligence.data.market_series_builder import (
    MarketSeriesBuilder,
)
from trading.context.trading_context import (
    TradingContext,
    TradingInstrument,
)
from intelligence.evidence.default_evidence_registry import (
    create_default_evidence_manager,
)
from intelligence.decision.default_decision_manager import (
    build_default_decision_manager,
)
from intelligence.execution_policy.default_execution_policy import (
    DefaultExecutionPolicy,
)

from intelligence.execution_policy.execution_policy_manager import (
    ExecutionPolicyManager,
)
from execution.broker.broker_result import (
    BrokerResult,
)
from execution.order_builder.order_request import (
    OrderRequest,
)

from execution.position_manager.position_manager import (
    PositionManager,
)

from execution.position_manager.position_monitor import (
    PositionMonitor,
)

from execution.position_manager.position_status import (
    PositionStatus,
)

from execution.order_builder.default_order_builder import (
    DefaultOrderBuilder,
)

from execution.risk_manager.default_risk_manager import (
    DefaultRiskManager,
)
from execution.trade_journal.trade_journal import (
    TradeJournal,
)
from execution.portfolio.portfolio_manager import (
    PortfolioManager,
)
from decision.recommendation.recommendation_engine import (
    RecommendationEngine,
)
from config.watchlist.watchlist_manager import WatchlistManager
from config.trading_config import TradingConfig
from tools.market_universe.universe_builder import UniverseBuilder

from trading.runtime.runtime_manager import RuntimeManager
from trading.suggestions.suggestion import (
    TradingSuggestion,
)

from trading.suggestions.suggestion_manager import (
    SuggestionManager,
)
from datetime import datetime
from backend.services.market_session_service import (
    MarketSessionService,
)
from market_data.market_data_engine import (
    MarketDataEngine,
)

from common.market_candle_cache import (
    MarketCandleCache,
)

logger = get_logger("RUSI")

class ExecutionManager:

    def __init__(
        self,
        config,
        logical_market_name=None,
    ):

        self._config = config
        self._trading_config = TradingConfig()
        self._watchlist = WatchlistManager()
        #
        # Evidence Runtime
        #
        self._evidence_manager = (
            create_default_evidence_manager()
        )
        self._market_session_service = (
            MarketSessionService()
        )
        #
        # Decision Runtime
        #
        self._decision_manager = (
            build_default_decision_manager()
        )
        #
        # Recommendation Engine
        #

        self._recommendation_engine = RecommendationEngine(
            self._trading_config
        )
        #
        # Execution Policy
        #

        self._execution_policy = (
            ExecutionPolicyManager(
                DefaultExecutionPolicy(
                    self._trading_config
                )
            )
        )
        #
        # Core Components
        #
        self._broker_manager = BrokerManager(config)

        #
        # Builders
        #
        self._snapshot_builder = MarketSnapshotBuilder()

        #
        # Intelligence
        #
        self._intelligence_manager = IntelligenceManager()

        #
        # Feature Engine
        #
        registry = create_default_feature_registry()

        self._feature_engine = FeatureEngine(registry)
        #
        # Order Builder
        #

        self._order_builder = DefaultOrderBuilder()

        #
        # Risk Manager
        #

        self._risk_manager = DefaultRiskManager()

        #
        # Position Manager
        #

        self._market_name = (
            logical_market_name
            if logical_market_name
            else self._config.market
        )

        #
        # NIFTY Real pending-order state.
        #
        # This is intentionally created only for the NIFTY F&O
        # execution manager so pending real orders cannot affect
        # MIDCAP, MCX, Stock Options, or Paper Trading.
        #
        self._nifty_real_pending_order = (
            NiftyRealPendingOrder()
            if self._market_name == "NIFTY_FNO"
            else None
        )

        #
        # NIFTY Real pending-exit state.
        #
        # This is intentionally isolated from the NIFTY Real
        # pending-entry state and from all other markets.
        #
        self._nifty_real_pending_exit_order = (
            NiftyRealPendingExitOrder()
            if self._market_name == "NIFTY_FNO"
            else None
        )

        #
        # Dedicated NIFTY Real P&L ledger.
        #
        # This is intentionally isolated from Paper Trading and
        # from the shared trade_journal.csv.
        #
        self._nifty_real_pnl_store = (
            NiftyRealPnlStore()
            if self._market_name == "NIFTY_FNO"
            else None
        )

        self._nifty_real_exit_monitor = None

        #
        # NIFTY Real consecutive complete-signal guard.
        #
        # Remembers only the last successfully executed NIFTY real
        # BUY signal. The state survives process restarts.
        #
        self._nifty_real_last_executed_signal_path = (
            Path(
                "runs/runtime/"
                "NIFTY_FNO_real_last_executed_signal.json"
            )
            if self._market_name == "NIFTY_FNO"
            else None
        )

        self._nifty_real_last_executed_signal = (
            self._load_nifty_real_last_executed_signal()
            if self._market_name == "NIFTY_FNO"
            else None
        )

        #
        # NIFTY Real Trading entry control.
        #
        # This controls NEW real broker entries only.
        # Existing positions must continue through the normal
        # monitoring / exit path.
        #
        # Preserve the current behavior until the API control
        # is explicitly introduced.
        #
        self._nifty_real_trading_control = (
            NiftyRealTradingControl()
            if self._market_name == "NIFTY_FNO"
            else None
        )

        self._nifty_real_trading_enabled = (
            self._nifty_real_trading_control.is_enabled()
            if self._nifty_real_trading_control is not None
            else False
        )

        logger.info(
            "NIFTY Real Trading Startup State : %s",
            "ENABLED"
            if self._nifty_real_trading_enabled
            else "DISABLED",
        )

        #
        # Position persistence isolation.
        #
        # NIFTY LIVE Real Trading must never restore or persist
        # positions from the legacy NIFTY_FNO Paper Trading state.
        #
        # Logical market remains NIFTY_FNO; only the persistence
        # namespace is separated.
        #
        position_persistence_market = (
            "NIFTY_FNO_REAL"
            if (
                self._config.execution_mode == ExecutionMode.LIVE
                and self._market_name == "NIFTY_FNO"
            )
            else self._market_name
        )

        self._position_manager = PositionManager(
            market_name=position_persistence_market,
        )

        #
        # Position Monitor
        #
        # Monitors existing OPEN option positions before
        # allowing a new trading decision.
        #

        self._position_monitor = PositionMonitor(
            self._position_manager,
            self._trading_config,
        )

        #
        # Portfolio Manager
        #

        self._portfolio_manager = PortfolioManager(
            self._position_manager.registry
        )
        #
        # Trade Journal
        #

        self._trade_journal = TradeJournal()

        #
        # Runtime Manager
        #
        self._runtime = RuntimeManager()

        #
        # Historical candle cache.
        #
        # Historical data is bootstrapped once and reused
        # across the 60-second execution cycles.
        #
        self._historical_candles = None

        #
        # Persistent Market Candle Cache
        #
        # Survives backend restarts and protects the broker
        # historical API from repeated bootstrap requests.
        #
        self._market_candle_cache = None

        #
        # AI Suggestion Manager
        #
        # Informational suggestions only.
        # This manager NEVER executes broker orders.
        #

        self._suggestion_manager = SuggestionManager()

    # ---------------------------------------------------------
    # NIFTY Real Trading Entry Control
    # ---------------------------------------------------------

    def _load_nifty_real_last_executed_signal(self):
        """
        Load the last successfully executed NIFTY real entry signal.
        """
        path = self._nifty_real_last_executed_signal_path

        if path is None or not path.exists():
            return None

        try:
            import json

            data = json.loads(path.read_text())

            if not isinstance(data, dict):
                return None

            signal = data.get("signal")

            if not isinstance(signal, dict):
                return None

            return signal

        except Exception as exc:
            logger.warning(
                "NIFTY Real Last Executed Signal : "
                "Unable to load persisted signal : %s",
                exc,
            )
            return None

    def _build_nifty_real_entry_signal(self, context):
        """
        Build the stable identity of the complete BUY signal.

        Dynamic values such as LTP, confidence and score are excluded.
        """
        recommendation = getattr(
            context,
            "recommendation",
            None,
        )

        decision = getattr(
            context,
            "decision",
            None,
        )

        order = getattr(
            context,
            "order",
            None,
        )

        decision_signal = getattr(
            decision,
            "signal",
            "",
        )

        decision_signal = getattr(
            decision_signal,
            "name",
            decision_signal,
        )

        try:
            strike = float(
                getattr(
                    recommendation,
                    "strike",
                    0.0,
                ) or 0.0
            )
        except (TypeError, ValueError):
            strike = 0.0

        return {
            "direction": str(decision_signal),
            "transaction_type": str(
                getattr(
                    order,
                    "transaction_type",
                    "",
                )
            ),
            "underlying_symbol": str(
                getattr(
                    recommendation,
                    "underlying_symbol",
                    "",
                ) or ""
            ),
            "option_symbol": str(
                getattr(
                    recommendation,
                    "option_symbol",
                    "",
                )
                or getattr(
                    order,
                    "symbol",
                    "",
                )
                or ""
            ),
            "option_token": str(
                getattr(
                    recommendation,
                    "option_token",
                    "",
                )
                or getattr(
                    order,
                    "token",
                    "",
                )
                or ""
            ),
            "exchange": str(
                getattr(
                    recommendation,
                    "exchange",
                    "",
                )
                or getattr(
                    order,
                    "exchange",
                    "",
                )
                or ""
            ),
            "expiry": str(
                getattr(
                    recommendation,
                    "expiry",
                    "",
                )
                or ""
            ),
            "strike": strike,
            "option_type": str(
                getattr(
                    recommendation,
                    "option_type",
                    "",
                )
                or ""
            ),
        }

    def _nifty_real_signal_is_same_as_last_executed(
        self,
        context,
    ):
        """
        Return True only when the complete current signal is identical
        to the last successfully executed signal.
        """
        previous = self._nifty_real_last_executed_signal

        if not previous:
            return False

        current = self._build_nifty_real_entry_signal(
            context
        )

        return current == previous

    def _save_nifty_real_last_executed_signal(
        self,
        context,
    ):
        """
        Persist the signal after confirmed broker execution.
        """
        path = self._nifty_real_last_executed_signal_path

        if path is None:
            return

        import json

        signal = self._build_nifty_real_entry_signal(
            context
        )

        try:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            payload = {
                "version": 1,
                "market": "NIFTY_FNO",
                "signal": signal,
            }

            tmp = path.with_suffix(".json.tmp")

            tmp.write_text(
                json.dumps(
                    payload,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )

            tmp.replace(path)

            self._nifty_real_last_executed_signal = signal

            logger.info(
                "NIFTY Real Last Executed Signal : "
                "Persisted | Option=%s | Token=%s | Direction=%s",
                signal["option_symbol"],
                signal["option_token"],
                signal["direction"],
            )

        except Exception as exc:
            logger.error(
                "NIFTY Real Last Executed Signal : "
                "Persistence failed : %s",
                exc,
            )

    def _nifty_real_eod_exit_due(self) -> bool:
        """
        NIFTY Real-only mandatory EOD boundary.

        At/after 15:15 IST:
          - new NIFTY Real entries are blocked
          - existing NIFTY Real positions are forced through
            the existing broker-confirmed exit path.

        This does not affect Paper Trading, MIDCPNIFTY,
        MCX, Equity, or the existing SL/profit-protection
        implementation.
        """
        if (
            self._config.execution_mode != ExecutionMode.LIVE
            or self._market_name != "NIFTY_FNO"
        ):
            return False

        now_ist = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        cutoff = now_ist.replace(
            hour=15,
            minute=15,
            second=0,
            microsecond=0,
        )

        return now_ist >= cutoff

    def set_nifty_real_trading_enabled(
        self,
        enabled: bool,
    ):
        """
        Enable or disable NEW NIFTY real-trading entries.

        This does not stop the execution engine and does not
        interfere with monitoring or exiting an existing position.
        """

        requested_enabled = bool(enabled)

        if self._market_name != "NIFTY_FNO":
            self._nifty_real_trading_enabled = False

            logger.warning(
                "NIFTY Real Trading control ignored for market : %s",
                self._market_name,
            )

            return False

        if self._nifty_real_trading_control is None:
            raise RuntimeError(
                "NIFTY Real Trading Control is not initialized."
            )

        self._nifty_real_trading_enabled = (
            self._nifty_real_trading_control.save(
                requested_enabled
            )
        )

        logger.info(
            "NIFTY Real Trading : %s",
            "ENABLED"
            if self._nifty_real_trading_enabled
            else "DISABLED",
        )

        return self._nifty_real_trading_enabled

    def is_nifty_real_trading_enabled(self):
        """
        Return whether NEW NIFTY real-trading entries are enabled.
        """

        return self._nifty_real_trading_enabled

    def get_nifty_real_trading_status(self):
        """
        Return the current NIFTY real-trading entry-control status.
        """

        return {
            "enabled": self._nifty_real_trading_enabled,
            "market": self._market_name,
            "new_entries_allowed": (
                self._nifty_real_trading_enabled
                and self._market_name == "NIFTY_FNO"
                and self._config.execution_mode == ExecutionMode.LIVE
            ),
        }

    # ---------------------------------------------------------
    # NIFTY Real Pending Order Reconciliation
    # ---------------------------------------------------------

    def _reconcile_nifty_real_pending_order(self):
        """
        Reconcile an already-submitted NIFTY real broker order.

        IMPORTANT:
        - This method NEVER places a new broker order.
        - It only checks the persisted broker Order ID.
        - A confirmed fill is returned to the caller for position
          creation using the actual broker fill quantity/price.
        - An unresolved order remains pending so the next cycle
          cannot submit a duplicate NIFTY entry.
        - This path is NIFTY_FNO only.
        """

        if self._market_name != "NIFTY_FNO":
            return {
                "state": "NOT_APPLICABLE",
                "pending": False,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_order": None,
            }

        pending_store = self._nifty_real_pending_order

        if pending_store is None:
            return {
                "state": "NOT_INITIALIZED",
                "pending": False,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_order": None,
            }

        pending = pending_store.load()

        if pending is None:
            return {
                "state": "NONE",
                "pending": False,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_order": None,
            }

        broker_order_id = str(
            pending.get("order_id") or ""
        ).strip()

        if not broker_order_id:
            logger.error(
                "NIFTY Real Pending Order : "
                "Persisted state has no broker Order ID"
            )

            return {
                "state": "INVALID",
                "pending": True,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_order": pending,
            }

        if self._nifty_real_order_executor is None:
            logger.error(
                "NIFTY Real Pending Order : "
                "Order executor is not initialized"
            )

            return {
                "state": "UNAVAILABLE",
                "pending": True,
                "broker_order_id": broker_order_id,
                "filled_quantity": 0,
                "average_price": None,
                "pending_order": pending,
            }

        logger.info(
            "NIFTY Real Pending Order : "
            "Checking existing broker Order ID %s",
            broker_order_id,
        )

        broker_status = (
            self._nifty_real_order_executor.check_existing_order(
                broker_order_id
            )
        )

        status = str(
            broker_status.get("status") or ""
        ).strip().lower()

        filled_quantity = int(
            broker_status.get("filled_quantity") or 0
        )

        average_price = broker_status.get(
            "average_price"
        )

        try:
            average_price = (
                float(average_price)
                if average_price is not None
                else None
            )
        except (TypeError, ValueError):
            average_price = None

        if (
            status in {
                "complete",
                "completed",
                "filled",
                "executed",
            }
            and filled_quantity > 0
            and average_price is not None
            and average_price > 0
        ):
            logger.info(
                "NIFTY Real Pending Order : "
                "BROKER FILL CONFIRMED | "
                "OrderID=%s | Qty=%d | AvgPrice=%.2f",
                broker_order_id,
                filled_quantity,
                average_price,
            )

            return {
                "state": "FILLED",
                "pending": True,
                "broker_order_id": broker_order_id,
                "filled_quantity": filled_quantity,
                "average_price": average_price,
                "pending_order": pending,
            }

        if status in {
            "rejected",
            "cancelled",
            "canceled",
            "failed",
            "expired",
        }:
            logger.warning(
                "NIFTY Real Pending Order : "
                "BROKER ORDER TERMINATED | "
                "OrderID=%s | Status=%s",
                broker_order_id,
                status,
            )

            return {
                "state": "REJECTED",
                "pending": True,
                "broker_order_id": broker_order_id,
                "filled_quantity": filled_quantity,
                "average_price": average_price,
                "pending_order": pending,
            }

        logger.info(
            "NIFTY Real Pending Order : "
            "Still unresolved | OrderID=%s | Status=%s",
            broker_order_id,
            status or "UNKNOWN",
        )

        return {
            "state": "PENDING",
            "pending": True,
            "broker_order_id": broker_order_id,
            "filled_quantity": filled_quantity,
            "average_price": average_price,
            "pending_order": pending,
        }

    # ---------------------------------------------------------
    # NIFTY Real Persisted Position Broker Reconciliation
    # ---------------------------------------------------------

    def _reconcile_nifty_real_persisted_positions(
        self,
        restored_positions,
    ):
        """
        Reconcile persisted NIFTY LIVE positions against the
        current Angel One broker position state.

        IMPORTANT:
        - NIFTY_FNO LIVE only.
        - Read-only broker query.
        - Never places an order.
        - Never modifies broker positions.
        - A persisted position is trusted only when the broker
          confirms the same symbol/exchange/token, direction,
          and quantity.
        - If the broker is flat for a persisted position, the
          local persisted position is stale and is removed.
        - If broker state cannot be retrieved safely, fail closed.
        """

        if (
            self._config.execution_mode != ExecutionMode.LIVE
            or self._market_name != "NIFTY_FNO"
        ):
            return restored_positions

        if not restored_positions:
            logger.info(
                "NIFTY Real Broker Reconciliation | "
                "No persisted positions to reconcile"
            )
            return restored_positions

        if self._broker_manager is None:
            raise RuntimeError(
                "NIFTY Real Broker Reconciliation failed: "
                "Broker manager is not initialized."
            )

        smartapi_client = getattr(
            self._broker_manager,
            "smartapi_client",
            None,
        )

        if smartapi_client is None:
            raise RuntimeError(
                "NIFTY Real Broker Reconciliation failed: "
                "SmartAPI client is not initialized."
            )

        logger.info(
            "NIFTY Real Broker Reconciliation | "
            "Checking %d persisted position(s) against Angel One",
            len(restored_positions),
        )

        broker_response = smartapi_client.get_positions()

        if not isinstance(broker_response, dict):
            raise RuntimeError(
                "NIFTY Real Broker Reconciliation failed: "
                "Invalid broker positions response."
            )

        broker_status = bool(
            broker_response.get("status")
        )

        if not broker_status:
            raise RuntimeError(
                "NIFTY Real Broker Reconciliation failed: "
                f"Broker returned unsuccessful response: "
                f"{broker_response}"
            )

        broker_positions = broker_response.get("data")

        if broker_positions is None:
            broker_positions = []

        if not isinstance(broker_positions, list):
            raise RuntimeError(
                "NIFTY Real Broker Reconciliation failed: "
                "Broker positions data is not a list."
            )

        def _norm(value):
            return str(value or "").strip().upper()

        def _to_int(value):
            try:
                return int(float(value or 0))
            except (TypeError, ValueError):
                return 0

        confirmed_positions = []

        for position in list(restored_positions):

            symbol = _norm(
                getattr(position, "symbol", "")
            )
            exchange = _norm(
                getattr(position, "exchange", "")
            )
            token = _norm(
                getattr(position, "token", "")
            )
            transaction_type = _norm(
                getattr(position, "transaction_type", "")
            )
            quantity = abs(
                _to_int(
                    getattr(position, "quantity", 0)
                )
            )

            broker_match = None

            for broker_position in broker_positions:

                if not isinstance(
                    broker_position,
                    dict,
                ):
                    continue

                broker_symbol = _norm(
                    broker_position.get("tradingsymbol")
                    or broker_position.get("symbol")
                )

                broker_exchange = _norm(
                    broker_position.get("exchange")
                )

                broker_token = _norm(
                    broker_position.get("symboltoken")
                    or broker_position.get("token")
                )

                if (
                    broker_symbol == symbol
                    and broker_exchange == exchange
                    and broker_token == token
                ):
                    broker_match = broker_position
                    break

            if broker_match is None:
                logger.warning(
                    "NIFTY Real Broker Reconciliation | "
                    "STALE LOCAL POSITION REMOVED | "
                    "Position=%s | Symbol=%s | Exchange=%s | "
                    "Token=%s | LocalQty=%d",
                    getattr(
                        position,
                        "position_id",
                        "",
                    ),
                    symbol,
                    exchange,
                    token,
                    quantity,
                )

                self._position_manager.remove_position(
                    getattr(
                        position,
                        "position_id",
                        "",
                    )
                )

                continue

            net_qty = _to_int(
                broker_match.get("netqty")
                or broker_match.get("netQty")
            )

            broker_buy_qty = _to_int(
                broker_match.get("buyqty")
                or broker_match.get("buyQty")
            )

            broker_sell_qty = _to_int(
                broker_match.get("sellqty")
                or broker_match.get("sellQty")
            )

            broker_transaction = _norm(
                broker_match.get("transactiontype")
                or broker_match.get("transaction_type")
            )

            broker_direction = (
                "BUY"
                if net_qty > 0
                else "SELL"
                if net_qty < 0
                else ""
            )

            expected_direction = transaction_type or "BUY"

            quantity_matches = (
                abs(net_qty) == quantity
            )

            direction_matches = (
                broker_direction == expected_direction
            )

            if (
                net_qty != 0
                and quantity_matches
                and direction_matches
            ):
                logger.info(
                    "NIFTY Real Broker Reconciliation | "
                    "POSITION CONFIRMED | "
                    "Position=%s | Symbol=%s | Exchange=%s | "
                    "Token=%s | LocalQty=%d | BrokerNetQty=%d | "
                    "BrokerTransaction=%s | BuyQty=%d | SellQty=%d",
                    getattr(
                        position,
                        "position_id",
                        "",
                    ),
                    symbol,
                    exchange,
                    token,
                    quantity,
                    net_qty,
                    broker_transaction or broker_direction,
                    broker_buy_qty,
                    broker_sell_qty,
                )

                confirmed_positions.append(position)

                continue

            logger.error(
                "NIFTY Real Broker Reconciliation | "
                "DIVERGENT LOCAL POSITION REMOVED FROM "
                "AUTOMATED MANAGEMENT | "
                "Position=%s | Symbol=%s | Exchange=%s | "
                "Token=%s | LocalQty=%d | BrokerNetQty=%d | "
                "ExpectedDirection=%s | BrokerTransaction=%s",
                getattr(
                    position,
                    "position_id",
                    "",
                ),
                symbol,
                exchange,
                token,
                quantity,
                net_qty,
                expected_direction,
                broker_transaction or broker_direction,
            )

            self._position_manager.remove_position(
                getattr(
                    position,
                    "position_id",
                    "",
                )
            )

        self._position_manager.persist_positions()

        logger.info(
            "NIFTY Real Broker Reconciliation | "
            "COMPLETE | Persisted=%d | Confirmed=%d | Removed=%d",
            len(restored_positions),
            len(confirmed_positions),
            len(restored_positions) - len(confirmed_positions),
        )

        return confirmed_positions

    # ---------------------------------------------------------
    # NIFTY Real Pending Exit Order Reconciliation
    # ---------------------------------------------------------

    def _reconcile_nifty_real_pending_exit_order(self):
        """
        Reconcile an already-submitted NIFTY real broker exit order.

        IMPORTANT:
        - This method NEVER places a new broker order.
        - It only checks the persisted broker exit Order ID.
        - A confirmed fill is returned to the caller for local
          position closure using the actual broker fill quantity/price.
        - An unresolved exit remains pending so the next cycle
          cannot submit a duplicate NIFTY SELL order.
        - A rejected/cancelled exit clears only the pending-exit state.
        - This path is NIFTY_FNO only.
        """

        if self._market_name != "NIFTY_FNO":
            return {
                "state": "NOT_APPLICABLE",
                "pending": False,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_exit": None,
            }

        pending_store = self._nifty_real_pending_exit_order

        if pending_store is None:
            return {
                "state": "NOT_INITIALIZED",
                "pending": False,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_exit": None,
            }

        pending = pending_store.load()

        if pending is None:
            return {
                "state": "NONE",
                "pending": False,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_exit": None,
            }

        broker_order_id = str(
            pending.get("exit_order_id") or ""
        ).strip()

        if not broker_order_id:
            logger.error(
                "NIFTY Real Pending Exit : "
                "Persisted state has no broker Exit Order ID"
            )

            return {
                "state": "INVALID",
                "pending": True,
                "broker_order_id": "",
                "filled_quantity": 0,
                "average_price": None,
                "pending_exit": pending,
            }

        if self._nifty_real_order_executor is None:
            logger.error(
                "NIFTY Real Pending Exit : "
                "Order executor is not initialized"
            )

            return {
                "state": "UNAVAILABLE",
                "pending": True,
                "broker_order_id": broker_order_id,
                "filled_quantity": 0,
                "average_price": None,
                "pending_exit": pending,
            }

        logger.info(
            "NIFTY Real Pending Exit : "
            "Checking existing broker Exit Order ID %s",
            broker_order_id,
        )

        broker_status = (
            self._nifty_real_order_executor.check_existing_order(
                broker_order_id
            )
        )

        status = str(
            broker_status.get("status") or ""
        ).strip().lower()

        filled_quantity = int(
            broker_status.get("filled_quantity") or 0
        )

        average_price = broker_status.get(
            "average_price"
        )

        try:
            average_price = (
                float(average_price)
                if average_price is not None
                else None
            )
        except (TypeError, ValueError):
            average_price = None

        if (
            status in {
                "complete",
                "completed",
                "filled",
                "executed",
            }
            and filled_quantity > 0
            and average_price is not None
            and average_price > 0
        ):
            logger.info(
                "NIFTY Real Pending Exit : "
                "BROKER EXIT FILL CONFIRMED | "
                "OrderID=%s | Qty=%d | AvgPrice=%.2f",
                broker_order_id,
                filled_quantity,
                average_price,
            )

            return {
                "state": "FILLED",
                "pending": True,
                "broker_order_id": broker_order_id,
                "filled_quantity": filled_quantity,
                "average_price": average_price,
                "pending_exit": pending,
            }

        if status in {
            "rejected",
            "cancelled",
            "canceled",
            "failed",
            "expired",
        }:
            logger.warning(
                "NIFTY Real Pending Exit : "
                "BROKER EXIT ORDER TERMINATED | "
                "OrderID=%s | Status=%s",
                broker_order_id,
                status,
            )

            return {
                "state": "REJECTED",
                "pending": True,
                "broker_order_id": broker_order_id,
                "filled_quantity": filled_quantity,
                "average_price": average_price,
                "pending_exit": pending,
            }

        logger.info(
            "NIFTY Real Pending Exit : "
            "Still unresolved | OrderID=%s | Status=%s",
            broker_order_id,
            status or "UNKNOWN",
        )

        return {
            "state": "PENDING",
            "pending": True,
            "broker_order_id": broker_order_id,
            "filled_quantity": filled_quantity,
            "average_price": average_price,
            "pending_exit": pending,
        }

    # ---------------------------------------------------------
    # NIFTY Real Trading Daily P&L
    # ---------------------------------------------------------

    def _recover_nifty_real_filled_pending_order(
        self,
        reconciliation,
    ):
        """
        Recover a confirmed NIFTY real broker fill into the local
        PositionManager using the ACTUAL broker fill quantity/price.

        IMPORTANT:
        - Never places a broker order.
        - Never fabricates fill information.
        - Uses the persisted pending-order metadata.
        - Uses actual broker filled quantity and average price.
        - Idempotent by broker Order ID.
        - NIFTY_FNO only.
        """

        if self._market_name != "NIFTY_FNO":
            return False

        if not reconciliation:
            return False

        if reconciliation.get("state") != "FILLED":
            return False

        pending = reconciliation.get("pending_order") or {}

        broker_order_id = str(
            reconciliation.get("broker_order_id") or ""
        ).strip()

        filled_quantity = int(
            reconciliation.get("filled_quantity") or 0
        )

        average_price = reconciliation.get(
            "average_price"
        )

        try:
            average_price = (
                float(average_price)
                if average_price is not None
                else None
            )
        except (TypeError, ValueError):
            average_price = None

        if not broker_order_id:
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Missing broker Order ID"
            )
            return False

        if filled_quantity <= 0:
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Invalid filled quantity | "
                "OrderID=%s | Qty=%s",
                broker_order_id,
                filled_quantity,
            )
            return False

        if average_price is None or average_price <= 0:
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Invalid average fill price | "
                "OrderID=%s | AvgPrice=%s",
                broker_order_id,
                average_price,
            )
            return False

        #
        # Idempotency:
        # If this broker Order ID is already represented by an
        # OPEN local position, do not create another position.
        #
        existing_positions = (
            self._position_manager.registry.open_positions()
        )

        for position in existing_positions:
            existing_order_id = str(
                getattr(position, "order_id", "") or ""
            ).strip()

            if existing_order_id == broker_order_id:
                logger.warning(
                    "NIFTY Real Pending Recovery : "
                    "Position already exists for OrderID=%s | "
                    "PositionID=%s | Duplicate creation skipped",
                    broker_order_id,
                    getattr(position, "position_id", ""),
                )

                if self._nifty_real_pending_order is not None:
                    self._nifty_real_pending_order.clear()

                return True

        symbol = str(
            pending.get("symbol") or ""
        ).strip()

        exchange = str(
            pending.get("exchange") or ""
        ).strip()

        token = str(
            pending.get("token") or ""
        ).strip()

        transaction_type = str(
            pending.get("transaction_type") or ""
        ).strip().upper()

        order_type = str(
            pending.get("order_type") or ""
        ).strip()

        product_type = str(
            pending.get("product_type") or ""
        ).strip()

        try:
            stop_loss = float(
                pending.get("stop_loss") or 0.0
            )
        except (TypeError, ValueError):
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Invalid stop loss | OrderID=%s",
                broker_order_id,
            )
            return False

        try:
            target_price = float(
                pending.get("target_price") or 0.0
            )
        except (TypeError, ValueError):
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Invalid target price | OrderID=%s",
                broker_order_id,
            )
            return False

        if (
            not symbol
            or not symbol.startswith("NIFTY")
            or symbol.startswith("MIDCPNIFTY")
        ):
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Invalid symbol | "
                "OrderID=%s | Symbol=%s",
                broker_order_id,
                symbol,
            )
            return False

        if exchange != "NFO":
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Invalid exchange | "
                "OrderID=%s | Exchange=%s",
                broker_order_id,
                exchange,
            )
            return False

        if not token:
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Missing token | OrderID=%s",
                broker_order_id,
            )
            return False

        if transaction_type != "BUY":
            logger.error(
                "NIFTY Real Pending Recovery : "
                "Unexpected transaction type | "
                "OrderID=%s | Transaction=%s",
                broker_order_id,
                transaction_type,
            )
            return False

        #
        # IMPORTANT:
        # Quantity is the ACTUAL broker fill quantity, not the
        # originally requested quantity.
        #
        order_request = OrderRequest(
            symbol=symbol,
            exchange=exchange,
            token=token,
            transaction_type=transaction_type,
            quantity=filled_quantity,
            execution_price=average_price,
            order_type=order_type,
            product_type=product_type,
        )

        broker_result = BrokerResult(
            success=True,
            order_id=broker_order_id,
            message=(
                "NIFTY real pending order fill recovered "
                "from broker"
            ),
            filled_quantity=filled_quantity,
            average_price=average_price,
        )

        logger.info(
            "NIFTY Real Pending Recovery : "
            "Creating local position from confirmed broker fill | "
            "OrderID=%s | Symbol=%s | Qty=%d | AvgPrice=%.2f",
            broker_order_id,
            symbol,
            filled_quantity,
            average_price,
        )

        try:
            position = self._position_manager.open_position(
                broker_result,
                order_request,
                stop_loss=stop_loss,
                target_price=target_price,
            )
        except Exception:
            logger.exception(
                "NIFTY Real Pending Recovery : "
                "Failed to create local position | "
                "OrderID=%s",
                broker_order_id,
            )
            return False

        if position is None:
            logger.error(
                "NIFTY Real Pending Recovery : "
                "PositionManager returned no position | "
                "OrderID=%s",
                broker_order_id,
            )
            return False

        #
        # Clear pending state only AFTER PositionManager has
        # successfully created and persisted the position.
        #
        if self._nifty_real_pending_order is not None:
            self._nifty_real_pending_order.clear()

        logger.info(
            "NIFTY Real Pending Recovery : "
            "RECOVERY COMPLETE | "
            "OrderID=%s | PositionID=%s | "
            "Qty=%d | AvgPrice=%.2f",
            broker_order_id,
            position.position_id,
            position.quantity,
            position.entry_price,
        )

        return True

    def _get_nifty_daily_realized_pnl(self):
        """
        Return today's realized P&L for NIFTY Real Trading only.

        IMPORTANT:
        - Reads only the dedicated NIFTY Real P&L ledger.
        - Does not read trade_journal.csv.
        - Paper Trading P&L cannot affect this guard.
        """

        if self._market_name != "NIFTY_FNO":
            return 0.0

        if self._nifty_real_pnl_store is None:
            logger.warning(
                "NIFTY Real P&L Store is not initialized."
            )
            return 0.0

        return float(
            self._nifty_real_pnl_store.get_daily_realized_pnl()
        )

    # ---------------------------------------------------------
    # Runtime Market Selection
    # ---------------------------------------------------------

    def select_market(
        self,
        market_name: str,
    ):
        """
        Select the logical market for the next execution cycle.

        The existing execution pipeline remains unchanged.
        WatchlistManager resolves the logical instrument and
        InstrumentResolver resolves the broker instrument later.
        """

        instrument = self._watchlist.select(
            market_name
        )

        logger.info(
            "Market Selected : %s | %s | %s",
            market_name,
            instrument.symbol,
            instrument.exchange,
        )

        return instrument

    def _close_nifty_real_position_after_fill(
        self,
        position,
        *,
        broker_order_id,
        filled_quantity,
        average_price,
        exit_reason,
    ):
        """
        Close a NIFTY real position only after confirmed broker fill.

        IMPORTANT:
        - Never fabricates fill information.
        - Requires the broker-confirmed fill quantity to cover the
          complete local position.
        - Does not send another broker order.
        """
        try:
            filled_quantity = int(filled_quantity)
        except (TypeError, ValueError):
            filled_quantity = 0

        try:
            average_price = float(average_price)
        except (TypeError, ValueError):
            average_price = 0.0

        required_quantity = int(
            getattr(position, "quantity", 0) or 0
        )

        if (
            filled_quantity <= 0
            or average_price <= 0
            or required_quantity <= 0
        ):
            logger.error(
                "NIFTY Real Exit : Invalid confirmed fill | "
                "Position=%s | Order ID=%s | "
                "FilledQty=%s | AvgPrice=%s | RequiredQty=%s",
                getattr(position, "position_id", ""),
                broker_order_id,
                filled_quantity,
                average_price,
                required_quantity,
            )
            return False

        if filled_quantity < required_quantity:
            logger.error(
                "NIFTY Real Exit : Partial fill NOT accepted for "
                "local position closure | Position=%s | "
                "Order ID=%s | FilledQty=%d | RequiredQty=%d",
                getattr(position, "position_id", ""),
                broker_order_id,
                filled_quantity,
                required_quantity,
            )
            return False

        entry_price = float(
            getattr(position, "entry_price", 0.0) or 0.0
        )

        realized_pnl = (
            average_price - entry_price
        ) * required_quantity

        position.current_price = average_price
        position.unrealized_pnl = 0.0
        position.realized_pnl = realized_pnl
        position.exit_time = datetime.now()
        position.exit_reason = str(
            exit_reason or "REAL_EXIT"
        )
        position.status = PositionStatus.CLOSED

        #
        # Record the confirmed real-trade P&L in the dedicated
        # NIFTY Real ledger.
        #
        # IMPORTANT:
        # - This executes only after broker fill confirmation.
        # - The broker exit Order ID makes the operation idempotent.
        # - Paper Trading does not use this ledger.
        #
        if self._nifty_real_pnl_store is None:
            raise RuntimeError(
                "NIFTY Real P&L Store is not initialized."
            )

        pnl_recorded = (
            self._nifty_real_pnl_store.record_closed_trade(
                position_id=str(position.position_id),
                exit_order_id=str(broker_order_id),
                symbol=str(position.symbol),
                quantity=filled_quantity,
                realized_pnl=realized_pnl,
                exit_reason=str(
                    exit_reason or "REAL_EXIT"
                ),
                exit_time=datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).isoformat(),
            )
        )

        logger.info(
            "NIFTY Real P&L Ledger : %s | "
            "Order ID=%s | Realized P&L=%.2f",
            "RECORDED" if pnl_recorded else "ALREADY RECORDED",
            broker_order_id,
            realized_pnl,
        )

        logger.info("")
        logger.info("===== NIFTY REAL POSITION CLOSED =====")
        logger.info(
            "Position ID : %s",
            position.position_id,
        )
        logger.info(
            "Broker Order ID : %s",
            broker_order_id,
        )
        logger.info(
            "Symbol : %s",
            position.symbol,
        )
        logger.info(
            "Exit Reason : %s",
            position.exit_reason,
        )
        logger.info(
            "Filled Quantity : %d",
            filled_quantity,
        )
        logger.info(
            "Exit Average Price : %.4f",
            average_price,
        )
        logger.info(
            "Realized P&L : %.2f",
            realized_pnl,
        )

        return True

    def _execute_nifty_real_exit(
        self,
        position,
        *,
        exit_reason,
    ):
        """
        Submit one NIFTY real SELL exit and process the broker result.

        This method is NIFTY_FNO LIVE only.
        """
        if (
            self._config.execution_mode != ExecutionMode.LIVE
            or self._market_name != "NIFTY_FNO"
        ):
            return {
                "status": "NOT_APPLICABLE",
                "closed": False,
            }

        if self._nifty_real_order_executor is None:
            raise RuntimeError(
                "NIFTY Real Order Executor is not initialized."
            )

        if self._nifty_real_pending_exit_order is None:
            raise RuntimeError(
                "NIFTY Real Pending Exit Order store is not initialized."
            )

        quantity = int(
            getattr(position, "quantity", 0) or 0
        )

        if quantity <= 0:
            logger.error(
                "NIFTY Real Exit : Invalid position quantity | "
                "Position=%s | Qty=%s",
                getattr(position, "position_id", ""),
                quantity,
            )
            return {
                "status": "INVALID",
                "closed": False,
            }

        current_price = float(
            getattr(position, "current_price", 0.0) or 0.0
        )

        order = OrderRequest(
            symbol=str(position.symbol),
            exchange=str(position.exchange),
            token=str(position.token),
            transaction_type="SELL",
            quantity=quantity,
            execution_price=current_price,
            order_type="MARKET",
            product_type="INTRADAY",
        )

        logger.info("")
        logger.info("===== NIFTY REAL EXIT ORDER =====")
        logger.info(
            "Position ID : %s",
            position.position_id,
        )
        logger.info(
            "Symbol      : %s",
            position.symbol,
        )
        logger.info(
            "Exchange    : %s",
            position.exchange,
        )
        logger.info(
            "Token       : %s",
            position.token,
        )
        logger.info(
            "Transaction : SELL",
        )
        logger.info(
            "Quantity    : %d",
            quantity,
        )
        logger.info(
            "Reason      : %s",
            exit_reason,
        )

        broker_result = (
            self._nifty_real_order_executor.place_order(
                order
            )
        )

        if (
            broker_result.success
            and broker_result.order_id
            and int(broker_result.filled_quantity or 0)
            >= quantity
            and broker_result.average_price is not None
            and float(broker_result.average_price) > 0
        ):
            closed = self._close_nifty_real_position_after_fill(
                position,
                broker_order_id=broker_result.order_id,
                filled_quantity=broker_result.filled_quantity,
                average_price=broker_result.average_price,
                exit_reason=exit_reason,
            )

            return {
                "status": "FILLED" if closed else "INVALID_FILL",
                "closed": closed,
                "broker_result": broker_result,
            }

        #
        # Confirmed partial fill:
        #
        # The broker has already filled part of this SELL order.
        # Never submit another full-quantity SELL automatically.
        # Persist the SAME broker Order ID so reconciliation keeps
        # this position blocked until the state is explicitly
        # resolved.
        #
        partial_filled_quantity = int(
            broker_result.filled_quantity or 0
        )

        if (
            broker_result.order_id
            and partial_filled_quantity > 0
            and partial_filled_quantity < quantity
        ):
            self._nifty_real_pending_exit_order.save(
                position_id=str(position.position_id),
                exit_order_id=str(broker_result.order_id),
                symbol=str(position.symbol),
                exchange=str(position.exchange),
                token=str(position.token),
                quantity=quantity,
                entry_price=float(position.entry_price),
                exit_reason=str(exit_reason),
                created_at=datetime.now().isoformat(),
            )

            logger.error(
                "NIFTY Real Pending Exit : "
                "PARTIAL SELL FILL | "
                "Position=%s | Order ID=%s | "
                "Filled=%d | Required=%d | "
                "Automatic duplicate SELL BLOCKED",
                position.position_id,
                broker_result.order_id,
                partial_filled_quantity,
                quantity,
            )

            return {
                "status": "PARTIAL_FILL",
                "closed": False,
                "broker_result": broker_result,
            }

        #
        # Accepted but unresolved:
        # persist the SAME broker Order ID and never submit
        # another SELL until reconciliation resolves it.
        #
        if (
            not broker_result.success
            and broker_result.order_id
            and str(
                broker_result.message or ""
            ).startswith(
                "NIFTY real order accepted but fill status"
            )
        ):
            self._nifty_real_pending_exit_order.save(
                position_id=str(position.position_id),
                exit_order_id=str(broker_result.order_id),
                symbol=str(position.symbol),
                exchange=str(position.exchange),
                token=str(position.token),
                quantity=quantity,
                entry_price=float(position.entry_price),
                exit_reason=str(exit_reason),
                created_at=datetime.now().isoformat(),
            )

            logger.warning(
                "NIFTY Real Pending Exit : "
                "Persisted accepted-but-unresolved SELL | "
                "Position=%s | Order ID=%s",
                position.position_id,
                broker_result.order_id,
            )

            return {
                "status": "PENDING",
                "closed": False,
                "broker_result": broker_result,
            }

        logger.warning(
            "NIFTY Real Exit : Broker SELL not confirmed | "
            "Position=%s | Order ID=%s | Message=%s",
            position.position_id,
            getattr(broker_result, "order_id", ""),
            getattr(broker_result, "message", ""),
        )

        return {
            "status": "REJECTED",
            "closed": False,
            "broker_result": broker_result,
        }

    def _reconcile_and_process_nifty_real_pending_exit(
        self,
        position,
    ):
        """
        Reconcile a persisted NIFTY real SELL.

        No new broker order is submitted from this method.
        """
        reconciliation = (
            self._reconcile_nifty_real_pending_exit_order()
        )

        status = str(
            reconciliation.get("state") or ""
        ).upper()

        if status == "NONE":
            return {
                "status": "NONE",
                "blocked": False,
                "closed": False,
            }

        if status == "FILLED":
            pending_exit = reconciliation.get(
                "pending_exit"
            ) or {}

            pending_position_id = str(
                pending_exit.get("position_id") or ""
            ).strip()

            if (
                pending_position_id
                and pending_position_id
                != str(position.position_id)
            ):
                # -------------------------------------------------
                # Pending exit belongs to a previous local position.
                #
                # This can legitimately happen when:
                #
                #   1. broker SELL is filled,
                #   2. broker net quantity becomes zero,
                #   3. broker-position reconciliation removes the
                #      old local position,
                #   4. a new position is subsequently created.
                #
                # NEVER apply the old exit to the new position.
                #
                # Instead, verify the pending symbol is flat at the
                # broker, finalize the old trade P&L idempotently,
                # clear the pending-exit state, and continue managing
                # the current position normally.
                # -------------------------------------------------

                pending_symbol = str(
                    pending_exit.get("symbol") or ""
                ).strip()

                pending_exchange = str(
                    pending_exit.get("exchange") or ""
                ).strip()

                pending_token = str(
                    pending_exit.get("token") or ""
                ).strip()

                pending_quantity = int(
                    pending_exit.get("quantity") or 0
                )

                filled_quantity = int(
                    reconciliation.get("filled_quantity") or 0
                )

                average_price = reconciliation.get(
                    "average_price"
                )

                try:
                    average_price = float(average_price)
                except (TypeError, ValueError):
                    average_price = 0.0

                if (
                    not pending_symbol
                    or not pending_exchange
                    or not pending_token
                    or pending_quantity <= 0
                    or filled_quantity < pending_quantity
                    or average_price <= 0
                ):
                    logger.error(
                        "NIFTY Real Pending Exit : "
                        "Mismatched pending exit has invalid "
                        "broker-fill metadata | "
                        "PendingPosition=%s | Current=%s",
                        pending_position_id,
                        position.position_id,
                    )
                    return {
                        "status": "INVALID",
                        "blocked": True,
                        "closed": False,
                    }

                # -------------------------------------------------
                # Verify the ORIGINAL pending-exit instrument is
                # actually flat at Angel One.
                #
                # This prevents us from clearing a pending exit
                # merely because a broker Order Book entry says
                # COMPLETE while an unexpected residual position
                # still exists.
                # -------------------------------------------------

                try:
                    broker_positions = (
                        self._broker_manager
                        .smartapi_client
                        .get_positions()
                    )
                except Exception as exc:
                    logger.exception(
                        "NIFTY Real Pending Exit : "
                        "Unable to verify broker position for "
                        "previous position | "
                        "Position=%s | Symbol=%s | Error=%s",
                        pending_position_id,
                        pending_symbol,
                        exc,
                    )
                    return {
                        "status": "BROKER_POSITION_UNAVAILABLE",
                        "blocked": True,
                        "closed": False,
                    }

                if not isinstance(broker_positions, dict):
                    logger.error(
                        "NIFTY Real Pending Exit : "
                        "Invalid broker position response | "
                        "Position=%s | ResponseType=%s",
                        pending_position_id,
                        type(broker_positions).__name__,
                    )
                    return {
                        "status": "BROKER_POSITION_INVALID",
                        "blocked": True,
                        "closed": False,
                    }

                if not broker_positions.get("status"):
                    logger.error(
                        "NIFTY Real Pending Exit : "
                        "Broker position query failed | "
                        "Position=%s | Response=%s",
                        pending_position_id,
                        broker_positions,
                    )
                    return {
                        "status": "BROKER_POSITION_FAILED",
                        "blocked": True,
                        "closed": False,
                    }

                broker_data = broker_positions.get("data") or []

                if not isinstance(broker_data, list):
                    logger.error(
                        "NIFTY Real Pending Exit : "
                        "Invalid broker position data | "
                        "Position=%s",
                        pending_position_id,
                    )
                    return {
                        "status": "BROKER_POSITION_INVALID",
                        "blocked": True,
                        "closed": False,
                    }

                matched_broker_position = None

                for broker_position in broker_data:
                    if not isinstance(broker_position, dict):
                        continue

                    broker_symbol = str(
                        broker_position.get(
                            "tradingsymbol"
                        )
                        or broker_position.get(
                            "tradingSymbol"
                        )
                        or ""
                    ).strip()

                    broker_exchange = str(
                        broker_position.get(
                            "exchange"
                        )
                        or ""
                    ).strip()

                    broker_token = str(
                        broker_position.get(
                            "symboltoken"
                        )
                        or broker_position.get(
                            "symbolToken"
                        )
                        or ""
                    ).strip()

                    if (
                        broker_symbol == pending_symbol
                        and broker_exchange == pending_exchange
                        and broker_token == pending_token
                    ):
                        matched_broker_position = (
                            broker_position
                        )
                        break

                broker_net_quantity = 0

                if matched_broker_position is not None:
                    try:
                        broker_net_quantity = int(
                            float(
                                matched_broker_position.get(
                                    "netqty",
                                    0,
                                )
                                or 0
                            )
                        )
                    except (
                        TypeError,
                        ValueError,
                    ):
                        logger.error(
                            "NIFTY Real Pending Exit : "
                            "Invalid broker net quantity | "
                            "Position=%s | Symbol=%s",
                            pending_position_id,
                            pending_symbol,
                        )
                        return {
                            "status": "BROKER_POSITION_INVALID",
                            "blocked": True,
                            "closed": False,
                        }

                # -------------------------------------------------
                # Broker confirms the ORIGINAL position is flat.
                # Finalize the old trade without touching the
                # CURRENT position.
                # -------------------------------------------------

                if broker_net_quantity == 0:
                    entry_price = float(
                        pending_exit.get(
                            "entry_price"
                        )
                        or 0.0
                    )

                    if entry_price <= 0:
                        logger.error(
                            "NIFTY Real Pending Exit : "
                            "Invalid pending entry price | "
                            "Position=%s | EntryPrice=%s",
                            pending_position_id,
                            entry_price,
                        )
                        return {
                            "status": "INVALID",
                            "blocked": True,
                            "closed": False,
                        }

                    realized_pnl = (
                        average_price - entry_price
                    ) * pending_quantity

                    exit_reason = str(
                        pending_exit.get(
                            "exit_reason"
                        )
                        or "REAL_EXIT"
                    )

                    broker_order_id = str(
                        reconciliation.get(
                            "broker_order_id"
                        )
                        or pending_exit.get(
                            "exit_order_id"
                        )
                        or ""
                    ).strip()

                    if not broker_order_id:
                        logger.error(
                            "NIFTY Real Pending Exit : "
                            "Missing broker exit Order ID | "
                            "Position=%s",
                            pending_position_id,
                        )
                        return {
                            "status": "INVALID",
                            "blocked": True,
                            "closed": False,
                        }

                    if self._nifty_real_pnl_store is None:
                        raise RuntimeError(
                            "NIFTY Real P&L Store is not initialized."
                        )

                    pnl_recorded = (
                        self._nifty_real_pnl_store
                        .record_closed_trade(
                            position_id=(
                                pending_position_id
                            ),
                            exit_order_id=(
                                broker_order_id
                            ),
                            symbol=pending_symbol,
                            quantity=pending_quantity,
                            realized_pnl=realized_pnl,
                            exit_reason=exit_reason,
                            exit_time=(
                                datetime.now(
                                    ZoneInfo(
                                        "Asia/Kolkata"
                                    )
                                ).isoformat()
                            ),
                        )
                    )

                    self._nifty_real_pending_exit_order.clear()

                    logger.info(
                        "NIFTY Real Pending Exit : "
                        "STALE POSITION EXIT FINALIZED | "
                        "PendingPosition=%s | "
                        "CurrentPosition=%s | "
                        "Symbol=%s | Qty=%d | "
                        "Entry=%.2f | Exit=%.2f | "
                        "RealizedP&L=%.2f | "
                        "P&L=%s | OrderID=%s",
                        pending_position_id,
                        position.position_id,
                        pending_symbol,
                        pending_quantity,
                        entry_price,
                        average_price,
                        realized_pnl,
                        (
                            "RECORDED"
                            if pnl_recorded
                            else "ALREADY RECORDED"
                        ),
                        broker_order_id,
                    )

                    return {
                        "status": "FILLED",
                        "blocked": False,
                        "closed": False,
                    }

                # -------------------------------------------------
                # Unexpected residual broker quantity.
                #
                # Do NOT clear the pending exit and do NOT touch
                # the current local position.
                # -------------------------------------------------

                logger.error(
                    "NIFTY Real Pending Exit : "
                    "BROKER POSITION STILL OPEN FOR "
                    "PREVIOUS POSITION | "
                    "PendingPosition=%s | CurrentPosition=%s | "
                    "Symbol=%s | BrokerNetQty=%d",
                    pending_position_id,
                    position.position_id,
                    pending_symbol,
                    broker_net_quantity,
                )

                return {
                    "status": "PREVIOUS_POSITION_STILL_OPEN",
                    "blocked": True,
                    "closed": False,
                }

            filled_quantity = int(
                reconciliation.get(
                    "filled_quantity",
                    0,
                )
                or 0
            )

            required_quantity = int(
                getattr(position, "quantity", 0) or 0
            )

            if filled_quantity < required_quantity:
                logger.error(
                    "NIFTY Real Pending Exit : "
                    "Confirmed broker fill is insufficient "
                    "for local closure | Position=%s | "
                    "Filled=%d | Required=%d",
                    position.position_id,
                    filled_quantity,
                    required_quantity,
                )
                return {
                    "status": "PARTIAL_FILL",
                    "blocked": True,
                    "closed": False,
                }

            closed = self._close_nifty_real_position_after_fill(
                position,
                broker_order_id=reconciliation.get(
                    "broker_order_id",
                    "",
                ),
                filled_quantity=filled_quantity,
                average_price=reconciliation.get(
                    "average_price"
                ),
                exit_reason=pending_exit.get(
                    "exit_reason",
                    "REAL_EXIT",
                ),
            )

            if closed:
                self._nifty_real_pending_exit_order.clear()

            return {
                "status": "FILLED" if closed else "INVALID_FILL",
                "blocked": not closed,
                "closed": closed,
            }

        if status == "REJECTED":
            logger.warning(
                "NIFTY Real Pending Exit : "
                "Broker rejected/cancelled previous SELL | "
                "Position=%s",
                position.position_id,
            )

            self._nifty_real_pending_exit_order.clear()

            return {
                "status": "REJECTED",
                "blocked": False,
                "closed": False,
            }

        #
        # PENDING / UNAVAILABLE / INVALID / NOT_INITIALIZED
        #
        # Never submit another SELL while the previous broker
        # Order ID cannot be conclusively resolved.
        #
        logger.warning(
            "NIFTY Real Pending Exit : "
            "Exit remains unresolved | Position=%s | Status=%s",
            position.position_id,
            status,
        )

        return {
            "status": status or "PENDING",
            "blocked": True,
            "closed": False,
        }

    def run(self):

        logger.info("Execution Started")
        logger.info("Application : %s", self._config.application_name)
        logger.info("Version     : %s", self._config.version)
        logger.info("Mode        : %s", self._config.execution_mode.value)
        logger.info("Datasource  : %s", self._config.datasource.value)
        logger.info("Market      : %s", self._config.market)

        logger.info("")

        #
        # Step 1
        #
        logger.info("Step 1 : Initialize Broker")

        self._broker_manager.initialize()

        #
        # NIFTY Real Order Executor
        #
        # Uses the same authenticated SmartAPI client created
        # by BrokerManager. This does not affect Paper Trading
        # or other market execution paths.
        #
        if (
            self._market_name == "NIFTY_FNO"
            and self._config.execution_mode == ExecutionMode.LIVE
        ):
            self._nifty_real_order_executor = (
                NiftyRealOrderExecutor(
                    self._broker_manager.smartapi_client
                )
            )
        else:
            self._nifty_real_order_executor = None

        #
        # Market Universe
        #
        logger.info("Building Market Universe")

        UniverseBuilder().build()

        logger.info("Market Universe Ready")

        logger.info("")

        logger.info("")

        #
        # Step 2
        #
        logger.info("Step 2 : Download Historical Data")

        # Get logical instrument
        # Get logical instrument
        logger.info(
            "ACTIVE MARKET BEFORE RUN : %s",
            self._watchlist.selected_market,
        )

        instrument = self._watchlist.current()

        logger.info(
            "ACTIVE LOGICAL INSTRUMENT : %s | %s",
            instrument.symbol,
            instrument.exchange,
        )
        # Resolve broker token
        from tools.market_universe.instrument_resolver import (
            InstrumentResolver,
        )

        resolver = InstrumentResolver()

        instrument = resolver.resolve(instrument)

        logger.info(
            "Resolved Instrument : %s | %s | %s",
            instrument.symbol,
            instrument.exchange,
            instrument.token,
        )

        # Create datasource using resolved instrument
        self._broker_manager.create_datasource(instrument)

        datasource = self._broker_manager.datasource

        #
        # Market Data Engine
        #

        market_data_engine = MarketDataEngine(
            datasource
        )

        #
        # Publish the current cycle's market-data engine
        # for paper-trading option LTP monitoring.
        #
        # This is kept outside TradingRuntimeState because
        # MarketDataEngine is a live runtime dependency.
        #

        self._runtime.set_market_data_engine(
            market_data_engine
        )

        #
        # NIFTY Real Exit Monitor
        #
        # This is created only for the NIFTY_FNO real-trading
        # execution path. It never replaces the Paper Trading
        # PositionMonitor and is never used by other markets.
        #
        if (
            self._market_name == "NIFTY_FNO"
            and self._nifty_real_order_executor is not None
            and self._nifty_real_pending_exit_order is not None
        ):
            self._nifty_real_exit_monitor = NiftyRealExitMonitor(
                market_data_engine=market_data_engine,
                order_executor=self._nifty_real_order_executor,
                pending_exit_store=self._nifty_real_pending_exit_order,
                trading_config=self._trading_config,
            )
        else:
            self._nifty_real_exit_monitor = None

        #
        # NIFTY Real Pending Order Reconciliation
        #
        # This runs after broker initialization and before
        # new-entry evaluation.
        #
        # It NEVER submits a new broker order.
        #

        nifty_real_pending_order_blocked = False

        if (
            self._config.execution_mode == ExecutionMode.LIVE
            and self._market_name == "NIFTY_FNO"
        ):
            pending_reconciliation = (
                self._reconcile_nifty_real_pending_order()
            )

            pending_state = str(
                pending_reconciliation.get("state") or ""
            ).upper()

            if pending_state == "FILLED":

                recovered = (
                    self._recover_nifty_real_filled_pending_order(
                        pending_reconciliation
                    )
                )

                if not recovered:
                    #
                    # Broker confirms a fill but local recovery
                    # failed. NEVER submit another order.
                    #
                    nifty_real_pending_order_blocked = True

            elif pending_state in {
                "PENDING",
                "UNAVAILABLE",
                "INVALID",
            }:

                #
                # Existing broker order remains unresolved.
                # New NIFTY entries remain blocked.
                #
                nifty_real_pending_order_blocked = True

            elif pending_state == "REJECTED":

                #
                # Broker definitively terminated the order.
                #
                if self._nifty_real_pending_order is not None:
                    self._nifty_real_pending_order.clear()

        #
        # Restore persisted OPEN positions.
        #
        # This happens before the existing-position check so
        # recovered positions enter the normal monitoring path.
        #

        restored_positions = (
            self._position_manager
            .restore_persisted_positions()
        )

        # -----------------------------------------------------
        # LIVE NIFTY broker reconciliation
        #
        # Never trust a persisted real position blindly.
        # Confirm it still exists at Angel One before allowing
        # it into automated position management.
        # -----------------------------------------------------

        restored_positions = (
            self._reconcile_nifty_real_persisted_positions(
                restored_positions
            )
        )

        if restored_positions:

            logger.info(
                "Persisted Position Recovery Complete | "
                "Market=%s | Positions=%d",
                self._config.market,
                len(restored_positions),
            )

        #
        # Existing position state.
        #
        # IMPORTANT:
        #
        # Position monitoring is intentionally performed AFTER
        # the current RUSI decision has been generated.
        #
        # At this stage we only remember whether a position
        # exists. The actual exit decision happens later after:
        #
        #   Market Data
        #       -> Features
        #       -> Evidence
        #       -> Decision
        #

        existing_open_positions = (
            self._position_manager
            .registry
            .open_positions()
        )

        if existing_open_positions:

            logger.info("")
            logger.info(
                "Existing OPEN Position Detected : %d",
                len(existing_open_positions),
            )

        #
        # =========================================================
        # HISTORICAL DATA + PERSISTENT CACHE
        # =========================================================
        #
        # Historical candles are persisted across backend restarts.
        #
        # This prevents every service restart from requesting a
        # complete one-day historical range from the broker API.
        #
        # The live LTP is still applied by CandleBuilder below.
        #

        end_time = datetime.now(UTC)

        #
        # Create persistent cache for the resolved instrument.
        #

        self._market_candle_cache = MarketCandleCache(
            symbol=instrument.symbol,
            token=instrument.token,
            interval="ONE_MINUTE",
        )

        #
        # ---------------------------------------------------------
        # Try persistent cache first.
        # ---------------------------------------------------------
        #

        cached_candles = (
            self._market_candle_cache.load()
        )

        if cached_candles:

            self._historical_candles = list(
                cached_candles
            )

            logger.info(
                "Persistent Candle Cache Loaded : %d candles",
                len(self._historical_candles),
            )

            logger.info(
                "Historical API Bootstrap Skipped : "
                "Persistent cache available"
            )

        #
        # ---------------------------------------------------------
        # Bootstrap from broker only when no cache exists.
        # ---------------------------------------------------------
        #

        if self._historical_candles is None:

            logger.info(
                "Historical Data : Initial bootstrap"
            )

            historical_bootstrap_days = 1

            start_time = (
                end_time
                - timedelta(
                    days=historical_bootstrap_days
                )
            )

            logger.info(
                "Historical Bootstrap : %d days | %s -> %s",
                historical_bootstrap_days,
                start_time,
                end_time,
            )

            try:

                candles = datasource.get_historical_data(
                    exchange=instrument.exchange,
                    token=instrument.token,
                    interval="ONE_MINUTE",
                    from_datetime=start_time,
                    to_datetime=end_time,
                )

            except Exception as exc:

                logger.error(
                    "Historical bootstrap failed: %s",
                    exc,
                )

                logger.warning(
                    "Historical data unavailable. "
                    "Skipping this execution cycle."
                )

                return

            if candles is None:

                logger.error(
                    "Historical download failed"
                )

                return

            raw_data = candles.get("data")

            if not raw_data:

                logger.error(
                    "Historical data download failed."
                )

                logger.error(
                    "Broker Response : %s",
                    candles,
                )

                return

            self._historical_candles = list(
                raw_data
            )

            #
            # Save successful broker response immediately.
            #

            cache_saved = (
                self._market_candle_cache.save(
                    self._historical_candles
                )
            )

            logger.info(
                "Historical Bootstrap Complete : %d candles",
                len(self._historical_candles),
            )

            logger.info(
                "Persistent Candle Cache Saved : %s",
                cache_saved,
            )

        #
        # ---------------------------------------------------------
        # Final historical dataset used by this cycle.
        # ---------------------------------------------------------
        #

        raw_data = self._historical_candles

        logger.info(
            "Historical Data Used : %d candles",
            len(raw_data),
        )

        #
        # IMPORTANT:
        #
        # Do NOT request another historical range every 60 seconds.
        #
        # Current market price is synchronized through:
        #
        #     MarketDataEngine -> live LTP
        #     CandleBuilder    -> current working candle
        #
        # This avoids unnecessary broker historical API calls.
        #

        # Live Market Data
        #

        live_market_data = (
            market_data_engine.get_live_ltp()
        )

        logger.info("")

        logger.info(
            "Live Market Data"
        )

        logger.info(
            "Data Status : %s",
            live_market_data.data_status,
        )

        logger.info(
            "Live Price  : %.2f",
            live_market_data.last_price,
        )
        #
        # Live Market Quote
        #

        live_market_quote = (
            market_data_engine.get_quote()
        )

        logger.info("")
        logger.info(
            "Live Market Quote"
        )

        logger.info(
            "Quote Status : %s",
            live_market_quote.get("status"),
        )

        logger.info(
            "Quote Time   : %s",
            live_market_quote.get(
                "received_time"
            ),
        )

        logger.info(
            "Quote Data   : %s",
            live_market_quote.get(
                "data"
            ),
        )
        #
        # Step 3
        #
        logger.info("")
        logger.info("Step 3 : Build Candle Objects")

        market_open_for_candle = (
            self._market_session_service.is_market_open(
                instrument.exchange
            )
        )

        logger.info(
            "Candle Live Price Allowed : %s",
            market_open_for_candle,
        )

        candle_objects = CandleBuilder.build(
            raw_data,
            live_price=(
                live_market_data.last_price
                if market_open_for_candle
                else None
            ),
        )

        logger.info(
            "Internal Candle Objects : %d",
            len(candle_objects),
        )

        #
        # ---------------------------------------------------------
        # Persist current candle state
        # ---------------------------------------------------------
        #
        # CandleBuilder has now synchronized the historical series
        # with the latest live LTP.
        #
        # Persist the resulting candle series so completed/current
        # candles survive backend restarts.
        #
        # This does NOT call the broker historical API.
        #

        if (
            self._market_candle_cache is not None
            and candle_objects
        ):

            cache_candles = []

            for candle in candle_objects:

                cache_candles.append(
                    [
                        candle.timestamp.isoformat(),
                        float(candle.open),
                        float(candle.high),
                        float(candle.low),
                        float(candle.close),
                        int(candle.volume),
                    ]
                )

            cache_saved = (
                self._market_candle_cache.merge_and_save(
                    cache_candles
                )
            )

            logger.info(
                "Rolling Candle Cache Updated : %s | Candles=%d",
                cache_saved,
                len(cache_candles),
            )

        #
        # Step 4
        #
        logger.info("")
        logger.info("Step 4 : Build Market Snapshot")

        snapshot = self._snapshot_builder.build(
            candle_objects
        )

        logger.info("Market Snapshot Created")

        latest = snapshot.latest_candle

        logger.info(
            "Latest Close : %.2f",
            latest.close,
        )

        #
        # Step 5
        #
        logger.info("")
        logger.info("Step 5 : Technical Indicators")

        logger.info("------------------------------")

        if snapshot.indicators.sma20 is not None:

            logger.info(
                "SMA20 : %.2f",
                snapshot.indicators.sma20,
            )

        if snapshot.indicators.sma50 is not None:

            logger.info(
                "SMA50 : %.2f",
                snapshot.indicators.sma50,
            )

        if snapshot.indicators.ema20 is not None:

            logger.info(
                "EMA20 : %.2f",
                snapshot.indicators.ema20,
            )

        if snapshot.indicators.ema50 is not None:

            logger.info(
                "EMA50 : %.2f",
                snapshot.indicators.ema50,
            )

        #
        # Step 6
        #
        logger.info("")
        logger.info("Step 6 : Intelligence Analysis")

        intelligence = self._intelligence_manager.analyze(
            snapshot
        )
        #
        # Step 7
        #

        logger.info("")
        logger.info("Step 7 : Feature Extraction")

        series = MarketSeriesBuilder.build(
            candle_objects
        )

        feature_store = self._feature_engine.calculate(
            series
        )

        logger.info(
            "Registered Feature Calculators : %d",
            self._feature_engine.feature_count(),
        )

        logger.info(
            "Calculated Features            : %d",
            feature_store.count(),
        )

        #
        # Trading Context
        #

        context = TradingContext(
            market_snapshot=snapshot
        )
        context.instrument = instrument

        context.features = feature_store
        #
        # Step 8
        #
        logger.info("")
        logger.info("Step 8 : Evidence Runtime")

        evidence_context = (
            self._evidence_manager.generate(
                feature_store
            )
        )

        context.evidence = evidence_context

        logger.info(
            "Evidence Providers      : %d",
            self._evidence_manager.provider_count,
        )

        logger.info(
            "Evidence Generated      : %d",
            evidence_context.count,
        )

        logger.info(
            "Trading Context Created"
        )
        #
        # Step 9
        #
        logger.info("")
        logger.info("Step 9 : Decision Runtime")

        decision = self._decision_manager.evaluate(
            context.evidence
        )

        context.decision = decision

        #
        # =========================================================
        # EXISTING POSITION INTELLIGENCE CHECK
        # =========================================================
        #
        # IMPORTANT:
        #
        # The current RUSI decision is now available.
        # Therefore an already-open position must be evaluated
        # against the current market alignment BEFORE a new
        # option recommendation/order is generated.
        #
        # PositionMonitor will eventually evaluate:
        #
        #   - live option LTP
        #   - current P&L
        #   - hard Stop Loss
        #   - Target
        #   - current market direction
        #   - decision confidence
        #   - market reversal
        #   - profit protection
        #
        # If the position remains OPEN, this execution cycle
        # must stop here and MUST NOT create another position.
        #

        existing_open_positions = (
            self._position_manager
            .registry
            .open_positions()
        )

        if existing_open_positions:

            logger.info("")
            logger.info(
                "===== EXISTING POSITION INTELLIGENCE CHECK ====="
            )

            logger.info(
                "Open Positions : %d",
                len(existing_open_positions),
            )

            logger.info(
                "Current Decision : %s",
                decision.signal.name,
            )

            logger.info(
                "Decision Confidence : %.2f",
                decision.confidence,
            )

            logger.info(
                "Decision Score : %.4f",
                decision.score,
            )

            #
            # NIFTY REAL EXIT PATH
            #
            # IMPORTANT:
            # - LIVE + NIFTY_FNO uses the dedicated real-exit path.
            # - Existing NIFTY positions are closed only after a
            #   confirmed broker SELL fill.
            # - A pending/unresolved broker SELL blocks any duplicate
            #   SELL submission.
            # - Paper Trading and all other markets continue through
            #   the existing PositionMonitor path unchanged.
            #

            if (
                self._config.execution_mode == ExecutionMode.LIVE
                and self._market_name == "NIFTY_FNO"
            ):

                logger.info(
                    "NIFTY Real Trading : "
                    "Using dedicated real exit monitoring"
                )

                for position in existing_open_positions:

                    if position.status.value != "OPEN":
                        continue

                    #
                    # Mandatory NIFTY Real EOD exit MUST have priority.
                    #
                    # IMPORTANT:
                    # - 15:15 IST is a mandatory exit boundary.
                    # - A previous-position pending SELL must NEVER delay
                    #   the current position's mandatory EOD exit.
                    # - This uses the SAME broker-confirmed exit path.
                    # - Existing SL/profit-protection/reversal logic is
                    #   completely untouched.
                    #

                    if self._nifty_real_eod_exit_due():

                        logger.warning(
                            "NIFTY Real EOD Exit Triggered | "
                            "15:15 IST cutoff reached | "
                            "Position=%s | Reason=EOD_EXIT",
                            position.position_id,
                        )

                        exit_result = (
                            self._execute_nifty_real_exit(
                                position,
                                exit_reason="EOD_EXIT",
                            )
                        )

                        logger.info(
                            "NIFTY Real EOD Exit Result | "
                            "Position=%s | Status=%s | Closed=%s",
                            position.position_id,
                            exit_result.get("status"),
                            exit_result.get("closed"),
                        )

                        continue

                    #
                    # First reconcile any previously submitted real
                    # SELL. This method NEVER submits a new order.
                    #

                    pending_exit_result = (
                        self._reconcile_and_process_nifty_real_pending_exit(
                            position
                        )
                    )

                    if pending_exit_result.get("blocked"):
                        logger.warning(
                            "NIFTY Real Exit : "
                            "New SELL blocked while previous "
                            "exit remains unresolved | Position=%s | "
                            "Status=%s",
                            position.position_id,
                            pending_exit_result.get("status"),
                        )
                        continue

                    #
                    # A confirmed pending SELL may already have closed
                    # the position. Do not evaluate another exit.
                    #

                    if position.status.value != "OPEN":
                        continue

                    #
                    # Existing NIFTY Real exit monitor.
                    # DO NOT CHANGE.
                    #

                    if self._nifty_real_exit_monitor is None:
                        raise RuntimeError(
                            "NIFTY Real Exit Monitor is not initialized."
                        )

                    exit_reason = (
                        self._nifty_real_exit_monitor.evaluate_exit_reason(
                            position,
                            decision=decision,
                        )
                    )

                    if not exit_reason:
                        logger.info(
                            "NIFTY Real Exit : "
                            "No exit condition triggered | "
                            "Position=%s",
                            position.position_id,
                        )
                        continue

                    logger.warning(
                        "NIFTY Real Exit Triggered | "
                        "Position=%s | Reason=%s",
                        position.position_id,
                        exit_reason,
                    )

                    exit_result = (
                        self._execute_nifty_real_exit(
                            position,
                            exit_reason=exit_reason,
                        )
                    )

                    logger.info(
                        "NIFTY Real Exit Result | "
                        "Position=%s | Status=%s | Closed=%s",
                        position.position_id,
                        exit_result.get("status"),
                        exit_result.get("closed"),
                    )

            else:

                #
                # Existing Paper / non-NIFTY monitoring path.
                # DO NOT change this behavior.
                #

                self._position_monitor.monitor(
                    market_data_engine,
                    decision=decision,
                )

            #
            # Persist the latest live position state after
            # monitoring updates current price, peak P&L,
            # protection, reversal counters, or closure.
            #

            self._position_manager.persist_positions()

            for position in existing_open_positions:

                if position.status.value == "CLOSED":

                    self._trade_journal.close(position)

            remaining_positions = (
                self._position_manager
                .registry
                .open_positions()
            )

            if remaining_positions:

                logger.info(
                    "Existing position remains OPEN."
                )

                logger.info(
                    "New trade generation skipped."
                )

                # -------------------------------------------------
                # MARKET-SPECIFIC RUNTIME POSITION PUBLICATION
                # -------------------------------------------------
                #
                # This execution path returns before the normal
                # end-of-cycle runtime publication.
                #
                # Publish the actual PositionRegistry state before
                # returning so the MIDCAP dashboard can display the
                # currently OPEN paper position.
                #
                # This does NOT change trading, monitoring, SL,
                # target, profit protection, or option selection.
                #

                runtime_position = remaining_positions[0]

                self._runtime.update_for_market(
                    self._watchlist.selected_market,

                    # -------------------------------------------------
                    # Preserve market runtime data on the early-return
                    # path when an existing position remains OPEN.
                    # -------------------------------------------------
                    snapshot=snapshot,
                    instrument=instrument,
                    data_status=live_market_data.data_status,
                    live_price=live_market_data.last_price,

                    # -------------------------------------------------
                    # Existing position state.
                    # -------------------------------------------------
                    position=runtime_position,
                    positions=(
                        self._position_manager
                        .registry
                        .all()
                    ),
                )

                logger.info(
                    "Trading Runtime Position Published | "
                    "Market=%s | Position=%s",
                    self._watchlist.selected_market,
                    getattr(
                        runtime_position,
                        "symbol",
                        None,
                    ),
                )

                return

            logger.info(
                "Existing position CLOSED."
            )

            logger.info(
                "Continuing with new-trade evaluation."
            )

        #
        # Recommendation and option resolution are intentionally
        # performed after the execution confidence gate.
        #
        # No CE/PE selection or option LTP lookup should happen
        # for a decision that cannot pass execution policy.
        #

        logger.info(
            "Decision Generated"
        )

        logger.info("")
        logger.info("--------------------------------")
        logger.info("Decision Summary")
        logger.info("--------------------------------")

        logger.info(
            "Signal      : %s",
            decision.signal.name,
        )

        logger.info(
            "Confidence  : %.2f",
            decision.confidence,
        )

        logger.info(
            "Score       : %.2f",
            decision.score,
        )

        logger.info("")
        logger.info("Reasons")
        logger.info("-------")

        for reason in decision.reasons:

            logger.info(
                "- %s",
                reason,
            )
        for result in intelligence.results:

            logger.info("")
            logger.info("--------------------------------")
            logger.info("%s", result.engine_name)
            logger.info("--------------------------------")

            logger.info(
                "Signal      : %s",
                result.signal,
            )

            logger.info(
                "Confidence  : %.2f",
                result.confidence,
            )

            if result.score is not None:

                logger.info(
                    "Score       : %.2f",
                    result.score,
                )

            if result.reasons:

                logger.info("")

                logger.info("Reasons")

                logger.info("-------")

                for reason in result.reasons:

                    logger.info(
                        "- %s",
                        reason,
                    )
        #
        # Step 10
        #

        logger.info("")
        logger.info("Step 10 : Execution Policy")

        policy = self._execution_policy.evaluate(
            context.decision
        )

        context.execution_policy = policy

        logger.info(
            "Trade Allowed : %s",
            policy.trade_allowed,
        )

        logger.info(
            "Reason        : %s",
            policy.reason,
        )

        #
        # Option recommendation / execution instrument.
        #
        # MIDCAP-ONLY OPTION PREVIEW
        #
        # This preview populates CE/PE, strike, token, lot size,
        # option LTP, SL and target for the MIDCAP board even when
        # execution policy blocks the trade.
        #
        # IMPORTANT:
        # - Does NOT bypass execution policy.
        # - Does NOT create an order.
        # - Does NOT change the 70% threshold.
        # - Does NOT affect NIFTY.
        #

        if (
            context.instrument.symbol.startswith("MIDCPNIFTY")
            and not policy.trade_allowed
        ):

            try:

                logger.info("")
                logger.info(
                    "MIDCAP Option Preview : Policy Blocked"
                )

                recommendation = (
                    self._recommendation_engine.generate(
                        context,
                        market_data_engine=market_data_engine,
                    )
                )

                context.recommendation = recommendation

                if recommendation is not None:

                    logger.info(
                        "MIDCAP Preview Option : %s",
                        getattr(
                            recommendation,
                            "option_symbol",
                            None,
                        ),
                    )

                    logger.info(
                        "MIDCAP Preview Type : %s",
                        getattr(
                            recommendation,
                            "option_type",
                            None,
                        ),
                    )

                    logger.info(
                        "MIDCAP Preview Strike : %s",
                        getattr(
                            recommendation,
                            "strike",
                            None,
                        ),
                    )

                    logger.info(
                        "MIDCAP Preview Token : %s",
                        getattr(
                            recommendation,
                            "option_token",
                            None,
                        ),
                    )

                    logger.info(
                        "MIDCAP Preview Entry : %s",
                        getattr(
                            recommendation,
                            "entry_price",
                            None,
                        ),
                    )

                    logger.info(
                        "MIDCAP Preview Stop : %s",
                        getattr(
                            recommendation,
                            "stop_loss",
                            None,
                        ),
                    )

                    logger.info(
                        "MIDCAP Preview Target : %s",
                        getattr(
                            recommendation,
                            "target_price",
                            None,
                        ),
                    )

            except Exception as exc:

                logger.exception(
                    "MIDCAP Option Preview Failed : %s",
                    exc,
                )

        if policy.trade_allowed:

            recommendation = (
                self._recommendation_engine.generate(
                    context,
                    market_data_engine=market_data_engine,
                )
            )

            context.recommendation = recommendation

            # -----------------------------------------------------
            # NIFTY REAL TRADING REFERENCE OPTION PRICE
            # -----------------------------------------------------
            # Capture the exact option LTP generated by the
            # RecommendationEngine before later execution-stage
            # price refresh.
            #
            # NIFTY Real Trading only. Paper Trading and other
            # markets are intentionally untouched.
            #
            if (
                self._config.execution_mode == ExecutionMode.LIVE
                and self._market_name == "NIFTY_FNO"
            ):
                try:
                    reference_price = float(
                        recommendation.entry_price
                    )
                except (TypeError, ValueError):
                    reference_price = 0.0

                if reference_price > 0:
                    context.metadata["nifty_real_reference_price"] = reference_price

                    logger.info(
                        "NIFTY Real Reference Option Price : %.2f",
                        reference_price,
                    )

            if (
                recommendation.exchange
                and recommendation.option_symbol
                and recommendation.option_token
            ):

                context.metadata["execution_instrument"] = (
                    TradingInstrument(
                        symbol=(
                            recommendation.option_symbol
                        ),
                        exchange=(
                            recommendation.exchange
                        ),
                        token=(
                            recommendation.option_token
                        ),
                        quantity=(
                            recommendation.lot_size
                        ),
                        order_type=(
                            context.instrument.order_type
                        ),
                        product_type=(
                            context.instrument.product_type
                        ),
                    )
                )

                logger.info(
                    "Execution Instrument : %s | %s | %s | LotSize=%d",
                    recommendation.exchange,
                    recommendation.option_symbol,
                    recommendation.option_token,
                    recommendation.lot_size,
                )

        else:

            logger.info(
                "Recommendation Skipped : "
                "Execution Policy"
            )

        logger.info("")
        logger.info("Step 11 : Market Session")

        exchange = context.instrument.exchange

        market_status = (
            self._market_session_service.get_market_status(
                exchange
            )
        )

        logger.info(
            "Exchange      : %s",
            exchange,
        )

        logger.info(
            "Market Status : %s",
            market_status,
        )

        logger.info("")
        logger.info("Step 12 : Order Builder")

        # ---------------------------------------------------------
        # NIFTY Real New-Entry Cutoff
        # ---------------------------------------------------------
        #
        # NFO remains market-OPEN until 15:30.
        # New NIFTY entries are blocked from 15:29 onward.
        #
        # The dedicated NIFTY Real Exit path is independent of
        # this Order Builder gate, so existing positions can
        # continue to exit normally.
        # ---------------------------------------------------------

        nifty_new_entry_allowed = True

        if self._market_name == "NIFTY_FNO":
            nifty_new_entry_allowed = (
                self._market_session_service
                .is_new_entry_allowed(
                    exchange,
                )
            )

            if self._nifty_real_eod_exit_due():
                nifty_new_entry_allowed = False

                logger.info(
                    "NIFTY Real EOD Policy : "
                    "NEW ENTRIES BLOCKED FROM 15:15 IST"
                )

            logger.info(
                "NIFTY New Entry Status : %s",
                (
                    "ALLOWED"
                    if nifty_new_entry_allowed
                    else "BLOCKED"
                ),
            )

        if (
            policy.trade_allowed
            and market_status == "OPEN"
            and nifty_new_entry_allowed
        ):

            order = self._order_builder.build(
                context
            )

            context.order = order

            logger.info(
                "Symbol      : %s",
                order.symbol,
            )

            logger.info(
                "Exchange    : %s",
                order.exchange,
            )

            logger.info(
                "Transaction : %s",
                order.transaction_type,
            )

            logger.info(
                "Quantity    : %d",
                order.quantity,
            )

        else:

            if not policy.trade_allowed:

                logger.info(
                    "Order Builder Skipped : Execution Policy"
                )

            elif market_status != "OPEN":

                logger.info(
                    "Order Builder Skipped : Market Closed"
                )

            elif (
                self._market_name == "NIFTY_FNO"
                and not nifty_new_entry_allowed
            ):

                logger.info(
                    "Order Builder Skipped : "
                    "NIFTY New Entry Cutoff"
                )

        logger.info("")
        logger.info("Step 13 : Risk Manager")

        if hasattr(context, "order"):

            risk = self._risk_manager.evaluate(
                context.order
            )

            context.risk_result = risk

            logger.info(
                "Trade Allowed : %s",
                risk.trade_allowed,
            )

            logger.info(
                "Reason        : %s",
                risk.reason,
            )

            logger.info(
                "Approved Qty  : %d",
                risk.approved_quantity,
            )

            if risk.warnings:

                logger.info("Warnings")

                for warning in risk.warnings:

                    logger.info(
                        "- %s",
                        warning,
                    )

        else:

            logger.info(
                "Risk Manager Skipped : No Order"
            )

        # ---------------------------------------------------------
        # Broker Execution
        # ---------------------------------------------------------

        logger.info("")
        logger.info("Step 14 : Broker Execution")

        #
        # Current open-position count.
        #
        # This is the actual execution registry used by the
        # ExecutionManager.
        #

        open_positions = len(
            self._position_manager.registry.open_positions()
        )

        max_open_positions = (
            self._trading_config.max_open_positions
        )

        logger.info(
            "Open Positions : %d / %d",
            open_positions,
            max_open_positions,
        )

        if (
            hasattr(context, "order")
            and hasattr(context, "risk_result")
            and context.risk_result.trade_allowed
        ):

            #
            # Position-limit protection.
            #
            # Never submit another order once the configured
            # maximum number of open positions is reached.
            #

            if open_positions >= max_open_positions:

                logger.info(
                    "Broker Execution Skipped : "
                    "Maximum open positions reached (%d/%d)",
                    open_positions,
                    max_open_positions,
                )

            else:

                #
                # NIFTY Real Trading entry protection.
                #
                # This applies only to LIVE NIFTY execution.
                # Paper Trading and other real markets are
                # intentionally unaffected.
                #
                # The manual enable/disable control blocks only
                # NEW broker entries. Existing positions continue
                # through the normal monitoring / exit path.
                #

                real_trading_disabled = (
                    self._config.execution_mode
                    == ExecutionMode.LIVE
                    and self._market_name == "NIFTY_FNO"
                    and not self._nifty_real_trading_enabled
                )

                if real_trading_disabled:

                    logger.info(
                        "Broker Execution Skipped : "
                        "NIFTY Real Trading is DISABLED"
                    )

                #
                # NIFTY Real Trading daily-loss protection.
                #

                daily_loss_guard_triggered = False
                broker_result = None

                if (
                    self._config.execution_mode
                    == ExecutionMode.LIVE
                    and self._market_name == "NIFTY_FNO"
                ):

                    daily_realized_pnl = (
                        self._get_nifty_daily_realized_pnl()
                    )

                    logger.info(
                        "NIFTY Real Trading Daily P&L : %.2f",
                        daily_realized_pnl,
                    )

                    if daily_realized_pnl <= -10000.0:

                        daily_loss_guard_triggered = True

                        logger.warning(
                            "NIFTY Real Trading BLOCKED : "
                            "Daily realized P&L %.2f <= -10000.00",
                            daily_realized_pnl,
                        )

                if daily_loss_guard_triggered:

                    logger.info(
                        "Broker Execution Skipped : "
                        "NIFTY daily loss limit reached"
                    )

                elif real_trading_disabled:

                    logger.info(
                        "Broker Execution Skipped : "
                        "NIFTY Real Trading is DISABLED"
                    )

                elif nifty_real_pending_order_blocked:

                    logger.info(
                        "Broker Execution Skipped : "
                        "NIFTY Real Pending Order is unresolved"
                    )

                else:

                    #
                    # NIFTY Real Trading adverse-entry slippage guard.
                    #
                    # Compare the recommendation-time option price against
                    # a fresh exact-option LTP immediately before the
                    # broker order.
                    #
                    # BUY option:
                    #   Falling price       -> favorable -> allow
                    #   Rising <= limit     -> allow
                    #   Rising > limit      -> block
                    #
                    # Paper Trading and other markets are untouched.
                    #
                    nifty_adverse_slippage_blocked = False

                    #
                    # NIFTY Real consecutive complete-signal guard.
                    #
                    # Reuse the existing entry-block flag so the
                    # established broker execution path remains intact.
                    #
                    if (
                        self._config.execution_mode == ExecutionMode.LIVE
                        and self._market_name == "NIFTY_FNO"
                        and self._nifty_real_signal_is_same_as_last_executed(
                            context
                        )
                    ):

                        nifty_adverse_slippage_blocked = True

                        current_signal = (
                            self._build_nifty_real_entry_signal(
                                context
                            )
                        )

                        logger.warning(
                            "NIFTY Real Entry BLOCKED : "
                            "SAME CONSECUTIVE COMPLETE SIGNAL | "
                            "Direction=%s | Option=%s | Token=%s | "
                            "Strike=%s | OptionType=%s",
                            current_signal["direction"],
                            current_signal["option_symbol"],
                            current_signal["option_token"],
                            current_signal["strike"],
                            current_signal["option_type"],
                        )

                    if (
                        self._config.execution_mode == ExecutionMode.LIVE
                        and self._market_name == "NIFTY_FNO"
                    ):

                        reference_price = (
                            context.metadata.get("nifty_real_reference_price")
                            if context.metadata is not None
                            else None
                        )

                        try:
                            reference_price = float(reference_price)
                        except (TypeError, ValueError):
                            reference_price = 0.0

                        if reference_price <= 0:
                            nifty_adverse_slippage_blocked = True

                            logger.warning(
                                "NIFTY Real Trading BLOCKED : "
                                "Reference option price unavailable"
                            )

                        else:

                            try:
                                fresh_ltp = market_data_engine.get_instrument_ltp(
                                    exchange=context.order.exchange,
                                    symbol=context.order.symbol,
                                    token=context.order.token,
                                )
                            except Exception as exc:
                                fresh_ltp = None

                                logger.warning(
                                    "NIFTY Real Trading BLOCKED : "
                                    "Fresh option LTP lookup failed : %s",
                                    exc,
                                )

                            if (
                                fresh_ltp is None
                                or fresh_ltp.last_price is None
                                or fresh_ltp.data_status != "LIVE"
                            ):

                                nifty_adverse_slippage_blocked = True

                                logger.warning(
                                    "NIFTY Real Trading BLOCKED : "
                                    "Fresh option LTP unavailable or not LIVE"
                                )

                            else:

                                try:
                                    fresh_price = float(fresh_ltp.last_price)
                                except (TypeError, ValueError):
                                    fresh_price = 0.0

                                if fresh_price <= 0:

                                    nifty_adverse_slippage_blocked = True

                                    logger.warning(
                                        "NIFTY Real Trading BLOCKED : "
                                        "Invalid fresh option LTP %.2f",
                                        fresh_price,
                                    )

                                else:

                                    adverse_slippage_percent = (
                                        (fresh_price - reference_price)
                                        / reference_price
                                    ) * 100.0

                                    max_adverse_slippage = float(
                                        self._trading_config
                                        .nifty_real_max_adverse_slippage_percent
                                    )

                                    logger.info(
                                        "NIFTY Real Entry Price Check : "
                                        "Reference=%.2f | Fresh=%.2f | "
                                        "Change=%.2f%% | MaxAdverse=%.2f%%",
                                        reference_price,
                                        fresh_price,
                                        adverse_slippage_percent,
                                        max_adverse_slippage,
                                    )

                                    if adverse_slippage_percent > max_adverse_slippage:

                                        nifty_adverse_slippage_blocked = True

                                        logger.warning(
                                            "NIFTY Real Trading BLOCKED : "
                                            "Adverse option-price movement %.2f%% "
                                            "exceeds %.2f%% limit",
                                            adverse_slippage_percent,
                                            max_adverse_slippage,
                                        )

                    if nifty_adverse_slippage_blocked:

                        broker_result = None

                        logger.info(
                            "Broker Execution Skipped : "
                            "NIFTY adverse entry slippage protection"
                        )

                    else:

                        if (
                            self._config.execution_mode == ExecutionMode.LIVE
                            and self._market_name == "NIFTY_FNO"
                        ):
                            if self._nifty_real_order_executor is None:
                                raise RuntimeError(
                                    "NIFTY Real Order Executor is not initialized."
                                )

                            logger.info(
                                "NIFTY Real Trading : "
                                "Using dedicated NIFTY Real Order Executor"
                            )

                            broker_result = self._nifty_real_order_executor.place_order(
                                context.order
                            )

                            #
                            # NIFTY Real accepted-but-unresolved order
                            # protection.
                            #
                            # The broker has accepted the order and
                            # returned an Order ID, but fill confirmation
                            # was not resolved within the bounded polling
                            # window.
                            #
                            # Persist the broker Order ID so the next
                            # cycle reconciles the SAME order instead of
                            # submitting a duplicate entry.
                            #
                            if (
                                not broker_result.success
                                and broker_result.order_id
                                and str(
                                    broker_result.message or ""
                                ).startswith(
                                    "NIFTY real order accepted but fill status"
                                )
                            ):

                                self._nifty_real_pending_order.save(
                                    order_id=broker_result.order_id,
                                    symbol=context.order.symbol,
                                    exchange=context.order.exchange,
                                    token=context.order.token,
                                    transaction_type=context.order.transaction_type,
                                    quantity=context.order.quantity,
                                    order_type=context.order.order_type,
                                    product_type=context.order.product_type,
                                    stop_loss=float(
                                        getattr(
                                            context.recommendation,
                                            "stop_loss",
                                            0.0,
                                        )
                                    ),
                                    target_price=float(
                                        getattr(
                                            context.recommendation,
                                            "target_price",
                                            0.0,
                                        )
                                    ),
                                    decision_signal=str(
                                        getattr(
                                            context.decision.signal,
                                            "name",
                                            context.decision.signal,
                                        )
                                    ),
                                    decision_score=float(
                                        context.decision.score
                                    ),
                                    decision_confidence=float(
                                        context.decision.confidence
                                    ),
                                )

                                logger.warning(
                                    "NIFTY Real Pending Order : "
                                    "Persisted accepted-but-unresolved "
                                    "broker Order ID %s",
                                    broker_result.order_id,
                                )

                        else:
                            broker_result = self._broker_manager.place_order(
                                context.order
                            )

                        context.broker_result = broker_result

                # Only create a position when broker execution
                # actually occurred and succeeded.
                #
                # If the NIFTY daily-loss guard blocked the order,
                # broker_result does not exist and position creation
                # must be skipped cleanly.
                #

                if (
                    not daily_loss_guard_triggered
                    and not real_trading_disabled
                    and broker_result is not None
                    and broker_result.success
                ):

                    position = (
                        self._position_manager.open_position(
                            broker_result,
                            context.order,
                            stop_loss=getattr(
                                context.recommendation,
                                "stop_loss",
                                0.0,
                            ),
                            target_price=getattr(
                                context.recommendation,
                                "target_price",
                                0.0,
                            ),
                        )
                    )

                    context.position = position

                    #
                    # Persist the complete NIFTY real BUY signal only
                    # after broker execution succeeded and the local
                    # position was created.
                    #
                    # This is intentionally NOT persisted when:
                    # - the AI merely generates a recommendation
                    # - the order is rejected
                    # - the order is accepted but fill is unresolved
                    #
                    if (
                        self._config.execution_mode == ExecutionMode.LIVE
                        and self._market_name == "NIFTY_FNO"
                    ):
                        self._save_nifty_real_last_executed_signal(
                            context
                        )

                    self._trade_journal.record(
                        context,
                        position,
                    )

                    # -------------------------------------------------
                    # Portfolio Summary
                    # -------------------------------------------------

                    portfolio = (
                        self._portfolio_manager.build_portfolio()
                    )

                    summary = (
                        self._portfolio_manager.summary()
                    )

                    logger.info("")
                    logger.info(
                        "Step 15 : Portfolio Manager"
                    )

                    logger.info(
                        "Open Positions : %d",
                        summary.open_positions,
                    )

                    logger.info(
                        "Invested Amount : %.2f",
                        summary.invested_amount,
                    )

                    logger.info(
                        "Market Value : %.2f",
                        summary.market_value,
                    )

                    logger.info(
                        "Unrealized PnL : %.2f",
                        summary.unrealized_pnl,
                    )

                elif (
                    not daily_loss_guard_triggered
                    and not real_trading_disabled
                ):

                    logger.info(
                        "Position Manager Skipped : "
                        "Broker execution failed"
                    )

                logger.info("")

                logger.info(
                    "Broker Result"
                )

                if broker_result is not None:
                    logger.info(
                        "Status      : %s",
                        broker_result.success,
                    )

                    logger.info(
                        "Order ID    : %s",
                        broker_result.order_id,
                    )

                    logger.info(
                        "Message     : %s",
                        broker_result.message,
                    )
                else:
                    logger.info(
                        "Status      : NOT EXECUTED"
                    )
                    logger.info(
                        "Order ID    : NONE"
                    )
                    logger.info(
                        "Message     : Broker execution was skipped"
                    )

        else:

            logger.info(
                "Broker Execution Skipped : "
                "No executable order"
            )

        logger.info("")
        logger.info("Feature Summary")
        logger.info("------------------------------")

        logger.info(
            "Registered Calculators : %d",
            self._feature_engine.feature_count(),
        )

        logger.info(
            "Calculated Features    : %d",
            feature_store.count(),
        )
        logger.info("")
        logger.info("Evidence Summary")
        logger.info("------------------------------")

        for evidence in context.evidence.evidences:

            logger.info(
                "%s : %s (%.2f)",
                evidence.feature_id,
                evidence.signal,
                evidence.confidence,
            )
        logger.info("")
        logger.info("========================================")
        logger.info("Execution Summary")
        logger.info("========================================")

        logger.info(
            "Successful Engines : %d",
            intelligence.successful_engines,
        )

        logger.info(
            "Failed Engines     : %d",
            intelligence.failed_engines,
        )

        logger.info(
            "Execution Time     : %.2f ms",
            intelligence.execution_time_ms,
        )
        logger.info("")
        logger.info("Execution Finished")

        #
        # Publish Runtime State
        #
        #
        #
        # Publish AI Trading Suggestion
        #
        # Converts the existing recommendation into the
        # informational suggestion layer used by Flutter.
        #
        # No broker order is created here.
        #

        if context.recommendation is not None:

            recommendation = context.recommendation

            #
            # Use option symbol when available.
            # Fall back to the existing underlying symbol.
            #

            suggestion_symbol = (
                recommendation.option_symbol
                if recommendation.option_symbol
                else recommendation.symbol
            )

            #
            # -----------------------------------------------------
            # Get ACTUAL live price for the suggested instrument
            # -----------------------------------------------------
            #
            # IMPORTANT:
            #
            # recommendation.entry_price
            #     = price used by Recommendation Engine
            #
            # suggestion_latest_price
            #     = actual current market LTP of the selected option
            #
            # For F&O suggestions we MUST use the actual option LTP.
            #

            suggestion_latest_price = (
                recommendation.entry_price
            )

            if (
                recommendation.exchange
                and recommendation.option_symbol
                and recommendation.option_token
            ):

                try:

                    suggestion_ltp = (
                        market_data_engine
                        .get_instrument_ltp(
                            exchange=(
                                recommendation.exchange
                            ),
                            symbol=(
                                recommendation.option_symbol
                            ),
                            token=(
                                recommendation.option_token
                            ),
                        )
                    )

                    if (
                        suggestion_ltp.last_price is not None
                        and suggestion_ltp.last_price > 0
                        and suggestion_ltp.data_status == "LIVE"
                    ):

                        suggestion_latest_price = (
                            float(
                                suggestion_ltp.last_price
                            )
                        )

                        #
                        # IMPORTANT:
                        #
                        # The selected option LTP is the real
                        # paper-trading entry price.
                        #
                        # Do NOT leave recommendation.entry_price
                        # as the underlying NIFTY price.
                        #

                        recommendation.entry_price = (
                            suggestion_latest_price
                        )

                        logger.info(
                            "OPTION ENTRY LTP : %s | %s | %s | %.2f",
                            recommendation.exchange,
                            recommendation.option_symbol,
                            recommendation.option_token,
                            suggestion_latest_price,
                        )

                    else:

                        logger.warning(
                            "Suggestion LTP unavailable : "
                            "%s | %s | %s",
                            recommendation.exchange,
                            recommendation.option_symbol,
                            recommendation.option_token,
                        )

                except Exception as exc:

                    logger.warning(
                        "Suggestion LTP lookup failed : %s",
                        exc,
                    )

            #
            # -----------------------------------------------------
            # Calculate suggestion trade plan from ACTUAL option LTP
            # -----------------------------------------------------
            #
            # Existing risk model:
            #
            #   Stop Loss = Entry - 1%
            #   Target    = Entry + 2%
            #   Risk      = 1%
            #   Reward    = 2%
            #   R:R       = 2.0
            #
            # IMPORTANT:
            #
            # These calculations are performed on the OPTION
            # PREMIUM, not on the underlying instrument price.
            #

            suggestion_entry_price = (
                suggestion_latest_price
            )

            #
            # Direction-aware option trade plan
            #
            # BUY:
            #   SL     = 1% below entry
            #   Target = 2% above entry
            #
            # SELL:
            #   SL     = 1% above entry
            #   Target = 2% below entry
            #

            #
            # RUSI V1 OPTION BUYING:
            #
            # Underlying SELL -> PE
            # Underlying BUY  -> CE
            #
            # The actual option transaction is always BUY.
            #
            suggestion_signal = (
                str(
                    recommendation.recommendation
                ).upper()
                if recommendation.recommendation
                else "HOLD"
            )

            #
            # RUSI V1 is an OPTION BUYING system.
            #
            # The underlying direction determines CE/PE.
            # The suggestion itself is always a BUY of that
            # selected option contract.
            #
            # Therefore the option premium trade plan is:
            #
            #   Entry  = option LTP
            #   SL     = Entry - 1%
            #   Target = Entry + 2%
            #
            # This is identical for both CE and PE.
            #

            #
            # RUSI V1 OPTION BUYING
            #
            # The underlying signal determines the option:
            #
            #   BUY  -> CE
            #   SELL -> PE
            #
            # But the actual option transaction is ALWAYS BUY.
            #
            # Therefore the premium risk plan is identical
            # for CE and PE:
            #
            #   Entry  = option LTP
            #   SL     = 25% below entry
            #   Target = 40% above entry
            #
            # R:R = 40 / 25 = 1.60
            #

            if suggestion_signal in ("BUY", "SELL"):

                suggestion_stop_loss = (
                    suggestion_entry_price
                    * (
                        1.0
                        - (
                            self._trading_config
                            .option_stop_loss_percent
                            / 100.0
                        )
                    )
                )

                configured_target_price = (
                    suggestion_entry_price
                    * (
                        1.0
                        + (
                            self._trading_config
                            .option_target_percent
                            / 100.0
                        )
                    )
                )

                suggestion_risk = abs(
                    suggestion_entry_price
                    - suggestion_stop_loss
                )

                minimum_reward = (
                    suggestion_risk
                    * self._trading_config.minimum_risk_reward
                )

                minimum_target_price = (
                    suggestion_entry_price
                    + minimum_reward
                )

                suggestion_target_price = max(
                    configured_target_price,
                    minimum_target_price,
                )

            else:

                #
                # HOLD should not normally reach the
                # suggestion manager.
                #
                suggestion_stop_loss = (
                    suggestion_entry_price
                )

                suggestion_target_price = (
                    suggestion_entry_price
                )

            suggestion_risk = abs(
                suggestion_entry_price
                - suggestion_stop_loss
            )

            suggestion_reward = abs(
                suggestion_target_price
                - suggestion_entry_price
            )

            suggestion_risk_reward = (
                suggestion_reward / suggestion_risk
                if suggestion_risk > 0
                else 0.0
            )

            logger.info(
                "Suggestion Trade Plan : "
                "Signal=%s | "
                "Entry=%.2f | "
                "SL=%.2f | "
                "Target=%.2f | "
                "R:R=%.2f",
                suggestion_signal,
                suggestion_entry_price,
                suggestion_stop_loss,
                suggestion_target_price,
                suggestion_risk_reward,
            )

            logger.info(
                "Suggestion Trade Plan : "
                "Entry=%.2f | SL=%.2f | Target=%.2f | R:R=%.2f",
                suggestion_entry_price,
                suggestion_stop_loss,
                suggestion_target_price,
                suggestion_risk_reward,
            )

            #
            # -----------------------------------------------------
            # Create suggestion
            # -----------------------------------------------------
            #

            suggestion = TradingSuggestion(

                category="F&O",

                symbol=suggestion_symbol,

                exchange=recommendation.exchange,

                #
                # Actual current option market price
                #
                latest_price=(
                    suggestion_latest_price
                ),

                #
                # RUSI V1 is an OPTION BUYING system.
                #
                # recommendation.recommendation represents
                # underlying direction:
                #
                #   BUY/BUY-side  -> CE
                #   SELL/SELL-side -> PE
                #
                # The actual option trade action is BUY.
                #
                signal="BUY",

                #
                # Option-based trade plan
                #
                entry_price=(
                    suggestion_entry_price
                ),

                stop_loss=(
                    suggestion_stop_loss
                ),

                target_price=(
                    suggestion_target_price
                ),

                risk_reward=(
                    suggestion_risk_reward
                ),

                #
                # AI decision information
                #
                confidence=(
                    recommendation.confidence
                ),

                score=(
                    recommendation.score
                ),

                reasons=list(
                    recommendation.reasons
                ),

                #
                # Selected option information
                #
                underlying_symbol=(
                    recommendation.underlying_symbol
                ),

                option_symbol=(
                    recommendation.option_symbol
                ),

                option_token=(
                    recommendation.option_token
                ),

                option_type=(
                    recommendation.option_type
                ),

                strike=(
                    recommendation.strike
                ),

                expiry=(
                    recommendation.expiry
                ),

                status="WATCHING",
            )

            #
            # Confidence <= 50% is automatically ignored
            # inside SuggestionManager.
            #

            self._suggestion_manager.publish(
                suggestion
            )

        #
        # Snapshot active suggestions for runtime state.
        #

        suggestions = (
            self._suggestion_manager.get_active()
        )
        #
        # Current LIVE LTP of the selected option.
        #
        # recommendation.entry_price has already been
        # replaced with the actual option LTP above when
        # the live option lookup succeeds.
        #
        option_live_price = None

        if (
            context.recommendation is not None
            and context.recommendation.option_symbol
        ):
            try:
                candidate_option_price = float(
                    context.recommendation.entry_price
                )

                if candidate_option_price > 0:
                    option_live_price = (
                        candidate_option_price
                    )

            except (
                TypeError,
                ValueError,
            ):
                option_live_price = None

        runtime_data = {
            "snapshot": snapshot,
            "intelligence": intelligence,
            "feature_store": feature_store,
            "evidence": context.evidence,
            "decision": context.decision,
            "recommendation": context.recommendation,
            "execution_policy": context.execution_policy,
            "instrument": instrument,
            "updated_time": datetime.now().isoformat(),
            "data_status": live_market_data.data_status,
            "live_price": live_market_data.last_price,
              "option_live_price": option_live_price,
            #
            # Active AI suggestions for Flutter
            #
            "suggestions": suggestions,
        }

        if "portfolio" in locals():
            runtime_data["portfolio"] = portfolio

        if "summary" in locals():
            runtime_data["portfolio_summary"] = summary

        if hasattr(context, "position"):
            runtime_data["position"] = context.position

        # -----------------------------------------------------
        # COMPLETE POSITION HISTORY
        # -----------------------------------------------------
        #
        # PositionRegistry retains both OPEN and CLOSED
        # positions. Publish the complete registry so the
        # dashboard can calculate today's execution summary
        # and display trade history without creating another
        # trade-tracking system.
        #

        runtime_data["positions"] = (
            self._position_manager
            .registry
            .all()
        )

        if hasattr(context, "order"):
            runtime_data["order"] = context.order

        if hasattr(context, "risk_result"):
            runtime_data["risk_result"] = context.risk_result

        if hasattr(context, "broker_result"):
            runtime_data["broker_result"] = context.broker_result

        self._runtime.update(**runtime_data)

        # -----------------------------------------------------
        # MARKET-SPECIFIC RUNTIME STATE
        # -----------------------------------------------------
        #
        # Preserve the existing runtime publication above for
        # backward compatibility and NIFTY V1.
        #
        # Publish the same completed cycle into the isolated
        # state for the currently selected logical market.
        #

        self._runtime.update_for_market(
            self._watchlist.selected_market,
            **runtime_data,
        )

        logger.info("Trading Runtime Updated")
