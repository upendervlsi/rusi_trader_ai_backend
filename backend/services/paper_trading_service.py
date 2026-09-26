"""
============================================================
RUSI Trader AI

Paper Trading Runtime Service
============================================================

Purpose:
    Automatic paper trading from the existing RuntimeState.

Rules:
    - Manual START required.
    - No real broker orders.
    - Only processes trading cycles during supported market hours.
    - Uses the selected OPTION CONTRACT premium.
    - Does NOT use the NIFTY underlying price as option entry price.
    - Automatically manages option premium SL / TARGET.
    - Configurable lot size.
    - Persists paper trades for verification.
    - Safe to start/stop repeatedly.
============================================================
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
from datetime import datetime, time as dt_time
from pathlib import Path
from zoneinfo import ZoneInfo

from intelligence.paper_trading.paper_trade import PaperTrade
from intelligence.paper_trading.paper_portfolio import PaperPortfolio
from intelligence.paper_trading.paper_portfolio_manager import (
    PaperPortfolioManager,
)
from intelligence.signals.signal_type import SignalType
from trading.runtime.runtime_manager import RuntimeManager
from backend.services.position_management.v2_position_manager import (
    V2PositionManager,
)


from common.logger import get_logger

IST = ZoneInfo("Asia/Kolkata")

logger = get_logger("RUSI")


class PaperTradingService:

    _instance = None
    _instance_lock = threading.Lock()

    # ========================================================
    # RUNTIME
    # ========================================================

    REFRESH_INTERVAL = 60

    INITIAL_CAPITAL = 100000.0

    # ========================================================
    # END-OF-DAY POSITION PROTECTION
    # ========================================================
    #
    # For paper-trading analysis we do not carry option
    # positions overnight.
    #
    # At or after 3:29 PM IST:
    #   - Existing option positions are force-closed.
    #   - New option entries are blocked.
    #
    EOD_EXIT_TIME = dt_time(
        15,
        29,
    )

    DATA_FILE = Path(
        "data/paper_trading/paper_trades.json"
    )

    # ========================================================
    # OPTION PAPER-TRADING CONFIGURATION
    # ========================================================

    #
    # NSE NIFTY option lot size.
    #
    DEFAULT_LOT_SIZE = 65

    #
    # Number of EXTRA lots added to the default one lot.
    #
    # Examples:
    #
    #   0 -> 65 quantity
    #   1 -> 130 quantity
    #   2 -> 195 quantity
    #   3 -> 260 quantity
    #
    EXTRA_LOTS = 1

    #
    # Option premium risk configuration.
    #
    # Example:
    #
    #   Premium = 100
    #
    #   SL     = 100 * (1 - 0.25) = 75
    #   Target = 100 * (1 + 0.40) = 140
    #

    # Option premium risk configuration.
    #
    # These percentages apply to the SELECTED OPTION PREMIUM,
    # never to the underlying NIFTY price.
    #
    # Example:
    #   Premium = 100
    #   SL      = 75
    #   Target  = 140
    #
    OPTION_STOP_LOSS_PCT = 0.25

    OPTION_TARGET_PCT = 0.40

    # ========================================================
    # SINGLETON
    # ========================================================

    def __new__(cls):

        with cls._instance_lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

                cls._instance._running = False
                cls._instance._thread = None
                cls._instance._lock = threading.RLock()

                cls._instance._runtime = RuntimeManager()

                cls._instance._portfolio = PaperPortfolio(
                    capital=cls.INITIAL_CAPITAL,
                    available_capital=cls.INITIAL_CAPITAL,
                )

                cls._instance._portfolio_manager = (
                    PaperPortfolioManager()
                )

                cls._instance._last_cycle_id = 0

                # ========================================================
                # V2 OBSERVATION METRICS
                # ========================================================
                #
                # Tracks option-premium movement without changing
                # V1 entry, stop-loss, target, or exit behavior.
                #
                # Keyed by the in-memory identity of the trade.
                #
                cls._instance._trade_metrics = {}

                cls._instance._load()

        return cls._instance

    # ========================================================
    # LOT SIZE
    # ========================================================

    @classmethod
    def _quantity(cls) -> int:

        extra_lots = max(
            0,
            int(cls.EXTRA_LOTS),
        )

        return (
            cls.DEFAULT_LOT_SIZE
            * (1 + extra_lots)
        )

    # ========================================================
    # START
    # ========================================================

    def start(self):

        with self._lock:

            if self._running:

                already_running = True

            else:

                self._running = True

                self._thread = threading.Thread(
                    target=self._run,
                    daemon=True,
                    name="PaperTradingRuntime",
                )

                self._thread.start()

                already_running = False

        if already_running:

            return self.status()

        return self.status()

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        with self._lock:

            self._running = False

        return self.status()

    # ========================================================
    # STATUS
    # ========================================================

    def status(self):

        with self._lock:

            running = self._running

            last_cycle_id = self._last_cycle_id

            capital = self._portfolio.capital

            available_capital = (
                self._portfolio.available_capital
            )

            realized_pnl = (
                self._portfolio.realized_pnl
            )

            open_trades = len(
                self._portfolio.open_trades
            )

            closed_trades = len(
                self._portfolio.closed_trades
            )

        return {

            "running": running,

            "market_open": self._market_open(),

            "last_cycle_id": last_cycle_id,

            "capital": capital,

            "available_capital": available_capital,

            "realized_pnl": realized_pnl,

            "open_trades": open_trades,

            "closed_trades": closed_trades,

            "lot_size": self.DEFAULT_LOT_SIZE,

            "extra_lots": self.EXTRA_LOTS,

            "quantity": self._quantity(),
        }

    # ========================================================
    # DASHBOARD READ-ONLY SNAPSHOT
    # ========================================================

    def dashboard_snapshot(self):
        """
        Return a read-only snapshot of the persistent
        paper-trading portfolio for dashboard consumption.

        No trading action is performed here.
        """

        with self._lock:

            return {
                "realized_pnl": float(
                    self._portfolio.realized_pnl
                ),

                "open_trades": list(
                    self._portfolio.open_trades
                ),

                "closed_trades": list(
                    self._portfolio.closed_trades
                ),
            }

    # ========================================================
    # RUNTIME LOOP
    # ========================================================

    def _run(self):

        print(
            "Paper Trading Runtime Started"
        )

        while self._running:

            try:

                if not self._market_open():

                    for _ in range(
                        self.REFRESH_INTERVAL
                    ):

                        if not self._running:
                            break

                        time.sleep(1)

                    continue

                self._process_cycle()

            except Exception as exc:

                print(
                    "Paper Trading Cycle Failed:",
                    exc,
                )

            for _ in range(
                self.REFRESH_INTERVAL
            ):

                if not self._running:
                    break

                time.sleep(1)

        print(
            "Paper Trading Runtime Stopped"
        )

    # ========================================================
    # OPTION POSITION CALCULATION
    # ========================================================

    @classmethod
    def _calculate_option_position(
        cls,
        premium: float,
    ) -> dict:
        """
        Calculate the paper position from the actual
        selected option premium.

        DEFAULT_LOT_SIZE = 65
        EXTRA_LOTS = additional lots

        Example:
            premium = 100
            EXTRA_LOTS = 0
                quantity = 65
                investment = 6500

            EXTRA_LOTS = 1
                quantity = 130
                investment = 13000
        """

        premium = float(premium)

        if premium <= 0:
            raise ValueError(
                "Option premium must be greater than zero."
            )

        extra_lots = max(
            0,
            int(cls.EXTRA_LOTS),
        )

        total_lots = (
            1 + extra_lots
        )

        quantity = (
            cls.DEFAULT_LOT_SIZE
            * total_lots
        )

        investment = (
            premium
            * quantity
        )

        stop_loss = (
            premium
            * (
                1.0
                - cls.OPTION_STOP_LOSS_PCT
            )
        )

        target_price = (
            premium
            * (
                1.0
                + cls.OPTION_TARGET_PCT
            )
        )

        risk = (
            premium
            - stop_loss
        )

        reward = (
            target_price
            - premium
        )

        risk_reward = (
            reward / risk
            if risk > 0
            else 0.0
        )

        return {
            "lots": total_lots,
            "extra_lots": extra_lots,
            "lot_size": cls.DEFAULT_LOT_SIZE,
            "quantity": quantity,
            "premium": round(
                premium,
                2,
            ),
            "investment": round(
                investment,
                2,
            ),
            "stop_loss": round(
                stop_loss,
                2,
            ),
            "target_price": round(
                target_price,
                2,
            ),
            "risk_reward": round(
                risk_reward,
                4,
            ),
        }

    # ========================================================
    # PROCESS ONE TRADING CYCLE
    # ========================================================

    def _is_eod_exit_time(self) -> bool:

        return (
            datetime.now(IST).time()
            >= self.EOD_EXIT_TIME
        )

    def _process_cycle(self):

        state = self._runtime.get_state()

        #
        # -----------------------------------------------------
        # EXISTING PAPER POSITION MONITORING
        # -----------------------------------------------------
        #
        # An existing paper position must be monitored
        # independently of the current AI recommendation.
        #
        # The position itself contains the authoritative
        # option symbol / token / exchange.
        #

        market_data_engine = (
            self._runtime.get_market_data_engine()
        )

        if self._portfolio.open_trades:

            if market_data_engine is None:
                print(
                    "PAPER TRADE WAITING | "
                    "MarketDataEngine unavailable"
                )
                return

            open_trade = (
                self._portfolio.open_trades[0]
            )

            try:

                live_option_ltp = (
                    market_data_engine
                    .get_instrument_ltp(
                        exchange=open_trade.exchange,
                        symbol=open_trade.option_symbol,
                        token=str(
                            open_trade.option_token
                        ),
                    )
                )

                live_status = getattr(
                    live_option_ltp,
                    "data_status",
                    None,
                )

                live_status_value = getattr(
                    live_status,
                    "value",
                    live_status,
                )

                live_price = getattr(
                    live_option_ltp,
                    "last_price",
                    None,
                )

                if (
                    live_price is None
                    or float(live_price) <= 0
                    or str(
                        live_status_value
                    ).upper() != "LIVE"
                ):
                    print(
                        "PAPER TRADE WAITING | "
                        "Existing option LTP unavailable | "
                        f"Symbol={open_trade.option_symbol}"
                    )
                    return

                current_price = float(
                    live_price
                )

                print(
                    "PAPER EXISTING TRADE LTP | "
                    f"Symbol={open_trade.option_symbol} | "
                    f"LTP={current_price:.2f}"
                )

                self._update_open_trades(
                    current_price,
                    state.recommendation,
                )

                #
                # Only one active paper trade.
                #
                if self._portfolio.open_trades:
                    return

                #
                # If the live price triggered SL/TARGET,
                # the position was closed. Continue below so
                # a fresh recommendation can be considered.
                #

            except Exception as exc:

                print(
                    "PAPER EXISTING TRADE LTP FAILED | "
                    f"Symbol={open_trade.option_symbol} | "
                    f"Error={exc}"
                )
                return

        #
        # -----------------------------------------------------
        # CURRENT RECOMMENDATION
        # -----------------------------------------------------
        #

        recommendation = state.recommendation

        if recommendation is None:
            return

        #
        # Prevent duplicate processing.
        #

        if (
            state.cycle_id > 0
            and state.cycle_id == self._last_cycle_id
        ):
            return

        if state.cycle_id > 0:
            self._last_cycle_id = state.cycle_id

        option_symbol = getattr(
            recommendation,
            "option_symbol",
            None,
        )

        if not option_symbol:
            return

        #
        # Resolve the selected option premium.
        #

        current_price = self._get_option_price(
            state,
            recommendation,
            option_symbol,
        )

        if (
            current_price is None
            or current_price <= 0
        ):
            print(
                "PAPER TRADE WAITING | "
                f"Option premium unavailable | "
                f"Symbol={option_symbol}"
            )
            return

        current_price = float(
            current_price
        )

        #
        # No existing position remains.
        # A new recommendation may now be processed.
        #

        #
        # Only one active paper trade.
        #

        if self._portfolio.open_trades:

            return

        #
        # -----------------------------------------------------
        # END-OF-DAY ENTRY BLOCK
        # -----------------------------------------------------
        #
        # Once the 3:29 PM IST analysis cutoff is reached,
        # do not create another option position.
        #
        if self._is_eod_exit_time():

            print(
                "PAPER EOD ENTRY BLOCK | "
                f"Time={datetime.now(IST).strftime('%H:%M:%S')} | "
                "No new option entry allowed"
            )

            return

        signal_text = str(
            recommendation.recommendation
        ).upper()

        if signal_text not in (
            "BUY",
            "SELL",
        ):

            return

        #
        # RUSI V1 is an OPTION BUYING system.
        #
        # Underlying direction:
        #
        #   BUY  -> selected CE
        #   SELL -> selected PE
        #
        # Actual transaction:
        #
        #   BUY the selected option contract.
        #

        signal = SignalType.BUY

        #
        # -----------------------------------------------------
        # OPTION PREMIUM SL / TARGET
        # -----------------------------------------------------
        #

        stop_loss = (
            current_price
            * (
                1.0
                - self.OPTION_STOP_LOSS_PCT
            )
        )

        target_price = (
            current_price
            * (
                1.0
                + self.OPTION_TARGET_PCT
            )
        )

        quantity = self._quantity()

        trade = PaperTrade(

            signal=signal,

            option_symbol=(
                recommendation.option_symbol
            ),

            option_token=(
                recommendation.option_token
            ),

            exchange=(
                recommendation.exchange
            ),

            strike=float(
                recommendation.strike
                or 0.0
            ),

            expiry=(
                recommendation.expiry
            ),

            option_type=(
                recommendation.option_type
            ),

            entry_price=current_price,

            quantity=quantity,

            stop_loss=float(
                stop_loss
            ),

            target_price=float(
                target_price
            ),

            status="OPEN",

            pnl=0.0,

            entry_time=datetime.now(IST),

            reason=(
                "Automatic paper trade | "
                f"Option={option_symbol} | "
                f"UnderlyingSignal={signal_text}"
            ),
        )

        self._portfolio_manager.add_trade(
            self._portfolio,
            trade,
        )

        print(
            "PAPER TRADE OPENED | "
            f"Option={option_symbol} | "
            f"UnderlyingSignal={signal_text} | "
            f"Transaction=BUY OPTION | "
            f"Premium={current_price:.2f} | "
            f"Quantity={quantity} | "
            f"SL={stop_loss:.2f} | "
            f"Target={target_price:.2f}"
        )

        self._save()

    # ========================================================
    # OPTION PRICE RESOLUTION
    # ========================================================

    @staticmethod
    def _get_option_price(
        state,
        recommendation,
        option_symbol: str,
    ) -> float | None:

        #
        # Priority 1:
        #
        # Use the LIVE option LTP published by the
        # trading runtime.
        #

        runtime_option_price = getattr(
            state,
            "option_live_price",
            None,
        )

        try:

            if (
                runtime_option_price is not None
                and float(runtime_option_price) > 0
            ):
                live_price = float(
                    runtime_option_price
                )

                print(
                    "PAPER OPTION LTP | "
                    f"Symbol={option_symbol} | "
                    f"LTP={live_price:.2f}"
                )

                return live_price

        except (
            TypeError,
            ValueError,
        ):

            pass

        #
        # Priority 2:
        #
        # If the recommendation itself publishes the selected
        # option premium, use it.
        #

        recommendation_price_fields = (
            "entry_price",
            "option_price",
            "option_premium",
            "premium",
            "last_price",
            "ltp",
        )

        for field_name in (
            recommendation_price_fields
        ):

            value = getattr(
                recommendation,
                field_name,
                None,
            )

            try:

                if value is not None:

                    value = float(value)

                    if value > 0:

                        return value

            except (
                TypeError,
                ValueError,
            ):

                pass

        #
        # Priority 2:
        #
        # Runtime snapshot option analysis.
        #

        snapshot = getattr(
            state,
            "snapshot",
            None,
        )

        if snapshot is None:

            return None

        analysis = getattr(
            snapshot,
            "analysis",
            None,
        )

        options = getattr(
            analysis,
            "options",
            None,
        ) if analysis is not None else None

        #
        # Option analyzer metadata.
        #

        metadata = getattr(
            options,
            "metadata",
            None,
        )

        if isinstance(
            metadata,
            dict,
        ):

            #
            # Direct symbol keyed data.
            #

            direct = metadata.get(
                option_symbol
            )

            price = (
                PaperTradingService
                ._extract_price_from_value(
                    direct
                )
            )

            if price is not None:

                return price

            #
            # Common metadata containers.
            #

            for container_key in (
                "options",
                "option_chain",
                "contracts",
                "instruments",
                "quotes",
                "prices",
            ):

                container = metadata.get(
                    container_key
                )

                if not isinstance(
                    container,
                    dict,
                ):

                    continue

                direct = container.get(
                    option_symbol
                )

                price = (
                    PaperTradingService
                    ._extract_price_from_value(
                        direct
                    )
                )

                if price is not None:

                    return price

        #
        # Priority 3:
        #
        # Some option-analysis implementations may publish
        # a list of contracts.
        #

        for container_name in (
            "options",
            "option_chain",
            "contracts",
        ):

            container = getattr(
                options,
                container_name,
                None,
            ) if options is not None else None

            if not isinstance(
                container,
                (list, tuple),
            ):

                continue

            for item in container:

                symbol = (
                    PaperTradingService
                    ._extract_symbol_from_value(
                        item
                    )
                )

                if symbol != option_symbol:

                    continue

                price = (
                    PaperTradingService
                    ._extract_price_from_value(
                        item
                    )
                )

                if price is not None:

                    return price

        #
        # DO NOT fall back to state.live_price or
        # recommendation.entry_price.
        #
        # Those can represent the underlying NIFTY price.
        #

        return None

    # ========================================================
    # EXTRACT PRICE
    # ========================================================

    @staticmethod
    def _extract_price_from_value(
        value,
    ) -> float | None:

        if value is None:

            return None

        #
        # Direct numeric value.
        #

        if isinstance(
            value,
            (int, float),
        ):

            price = float(value)

            if price > 0:

                return price

            return None

        #
        # Dictionary.
        #

        if isinstance(
            value,
            dict,
        ):

            for key in (
                "option_price",
                "option_premium",
                "last_price",
                "ltp",
                "price",
                "close",
                "last",
                "value",
            ):

                candidate = value.get(
                    key
                )

                try:

                    if candidate is not None:

                        candidate = float(
                            candidate
                        )

                        if candidate > 0:

                            return candidate

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

            return None

        #
        # Object.
        #

        for key in (
            "option_price",
            "option_premium",
            "last_price",
            "ltp",
            "price",
            "close",
            "last",
            "value",
        ):

            candidate = getattr(
                value,
                key,
                None,
            )

            try:

                if candidate is not None:

                    candidate = float(
                        candidate
                    )

                    if candidate > 0:

                        return candidate

            except (
                TypeError,
                ValueError,
            ):

                pass

        return None

    # ========================================================
    # EXTRACT SYMBOL
    # ========================================================

    @staticmethod
    def _extract_symbol_from_value(
        value,
    ) -> str | None:

        if value is None:

            return None

        if isinstance(
            value,
            dict,
        ):

            for key in (
                "option_symbol",
                "symbol",
                "tradingsymbol",
                "instrument",
            ):

                symbol = value.get(
                    key
                )

                if symbol:

                    return str(symbol)

            return None

        for key in (
            "option_symbol",
            "symbol",
            "tradingsymbol",
            "instrument",
        ):

            symbol = getattr(
                value,
                key,
                None,
            )

            if symbol:

                return str(symbol)

        return None

    # ========================================================
    # UPDATE OPEN TRADES
    # ========================================================

    def _update_open_trades(
        self,
        current_price: float,
        recommendation=None,
    ):

        index = (
            len(
                self._portfolio.open_trades
            )
            - 1
        )

        changed = False

        while index >= 0:

            trade = (
                self._portfolio.open_trades[
                    index
                ]
            )

            pnl = self._calculate_pnl(
                trade,
                current_price,
            )

            #
            # V2 observation only.
            #
            # This records how far the option moved during
            # the life of the trade. It does NOT influence
            # the V1 stop-loss or target decision.
            #
            metrics = self._update_trade_metrics(
                trade,
                current_price,
            )

            #
            # -------------------------------------------------
            # V2 POSITION MANAGEMENT
            # -------------------------------------------------
            #
            # V2 consumes the existing RUSI recommendation
            # and the freshly updated MFE/MAE metrics.
            #
            # V2 does NOT replace the V1 hard stop or target.
            #

            v2_decision = V2PositionManager.evaluate(
                trade=trade,
                current_price=current_price,
                mfe_pct=float(
                    metrics.get(
                        "max_profit_pct",
                        0.0,
                    )
                ),
                mae_pct=float(
                    metrics.get(
                        "max_drawdown_pct",
                        0.0,
                    )
                ),
                recommendation=recommendation,
            )

            print(
                "PAPER V2 POSITION DECISION | "
                f"Symbol={trade.option_symbol} | "
                f"Action={v2_decision.action} | "
                f"Move={v2_decision.current_move_pct:.2f}% | "
                f"MFE={v2_decision.mfe_pct:.2f}% | "
                f"MAE={v2_decision.mae_pct:.2f}% | "
                f"RUSI={v2_decision.recommendation} | "
                f"Confidence={v2_decision.confidence:.2f} | "
                f"Score={v2_decision.score:.2f} | "
                f"Reason={v2_decision.reason}"
            )

            #
            # V2 exits become an exit condition.
            # V1 hard SL / TARGET remain below as the
            # authoritative safety backstop.
            #

            v2_closed = (
                v2_decision.action
                in (
                    "EARLY_LOSS_EXIT",
                    "PROFIT_PROTECTION_EXIT",
                )
            )

            #
            # -------------------------------------------------
            # END-OF-DAY POSITION PROTECTION
            # -------------------------------------------------
            #
            # Never carry an option position overnight.
            #
            # 3:29 PM IST is our analysis cutoff.
            #
            eod_closed = (
                self._is_eod_exit_time()
            )

            if eod_closed:
                print(
                    "PAPER EOD POSITION EXIT | "
                    f"Time={datetime.now(IST).strftime('%H:%M:%S')} | "
                    f"Symbol={trade.option_symbol} | "
                    f"Entry={trade.entry_price:.2f} | "
                    f"Exit={current_price:.2f} | "
                    f"P&L={pnl:.2f}"
                )

            #
            # RUSI V1 paper trading is
            # OPTION BUYING only.
            #
            # EOD exit has priority over V2 and V1.
            #
            closed = (
                eod_closed
                or
                v2_closed
                or
                current_price
                >= trade.target_price
                or
                current_price
                <= trade.stop_loss
            )

            #
            # PaperTrade is frozen, so the live current_price
            # must be represented by a replacement object.
            #
            if not closed:

                updated_trade = PaperTrade(

                    signal=trade.signal,

                    option_symbol=(
                        trade.option_symbol
                    ),

                    option_token=(
                        trade.option_token
                    ),

                    exchange=(
                        trade.exchange
                    ),

                    strike=(
                        trade.strike
                    ),

                    expiry=(
                        trade.expiry
                    ),

                    option_type=(
                        trade.option_type
                    ),

                    entry_price=(
                        trade.entry_price
                    ),

                    quantity=(
                        trade.quantity
                    ),

                    stop_loss=(
                        trade.stop_loss
                    ),

                    target_price=(
                        trade.target_price
                    ),

                    status=(
                        trade.status
                    ),

                    pnl=pnl,

                    current_price=(
                        current_price
                    ),

                    reason=(
                        trade.reason
                    ),

                    entry_time=(
                        trade.entry_time
                    ),

                    exit_time=(
                        trade.exit_time
                    ),
                )

                self._portfolio.open_trades[
                    index
                ] = updated_trade

                changed = True

                index -= 1
                continue

            if closed:

                if eod_closed:

                    status = "EOD_EXIT"

                elif v2_closed:

                    status = v2_decision.action

                elif (
                    current_price
                    >= trade.target_price
                ):
                    status = "TARGET"

                else:
                    status = "STOP_LOSS"

                closed_trade = PaperTrade(

                    signal=trade.signal,

                    option_symbol=(
                        trade.option_symbol
                    ),

                    option_token=(
                        trade.option_token
                    ),

                    exchange=(
                        trade.exchange
                    ),

                    strike=(
                        trade.strike
                    ),

                    expiry=(
                        trade.expiry
                    ),

                    option_type=(
                        trade.option_type
                    ),

                    entry_price=(
                        trade.entry_price
                    ),

                    quantity=(
                        trade.quantity
                    ),

                    stop_loss=(
                        trade.stop_loss
                    ),

                    target_price=(
                        trade.target_price
                    ),

                    status=status,

                    pnl=pnl,

                    current_price=(
                        current_price
                    ),

                    entry_time=(
                        trade.entry_time
                    ),

                    exit_time=datetime.now(IST),

                    reason=(
                        "EOD position protection: "
                        "option position force-closed at "
                        "3:29 PM IST to prevent overnight carry"
                        if eod_closed
                        else (
                            v2_decision.reason
                            if v2_closed
                            else trade.reason
                        )
                    ),
                )

                self._portfolio.closed_trades.append(
                    closed_trade
                )

                self._portfolio.realized_pnl += pnl

                # Use the same stable logical identity used
                # by _update_trade_metrics().
                entry_time = getattr(trade, "entry_time", None)

                if hasattr(entry_time, "isoformat"):
                    entry_time_key = entry_time.isoformat()
                else:
                    entry_time_key = str(entry_time)

                trade_metrics_key = (
                    f"{trade.exchange}|"
                    f"{trade.option_token}|"
                    f"{entry_time_key}|"
                    f"{trade.entry_price}"
                )

                self._trade_metrics.pop(
                    trade_metrics_key,
                    None,
                )

                del self._portfolio.open_trades[
                    index
                ]

                changed = True

                print(
                    "PAPER TRADE CLOSED | "
                    f"Status={status} | "
                    f"Option={trade.option_symbol} | "
                    f"EntryPremium={trade.entry_price:.2f} | "
                    f"ExitPremium={current_price:.2f} | "
                    f"Quantity={trade.quantity} | "
                    f"PnL={pnl:.2f}"
                )

            index -= 1

        if changed:
            self._save()

    # ========================================================
    # V2 OBSERVATION METRICS
    # ========================================================

    def _update_trade_metrics(
        self,
        trade,
        current_price: float,
    ):
        """
        Observation-only metrics.

        IMPORTANT:
            This does NOT modify V1 exit behavior.
            Existing 25% stop-loss and 40% target remain
            authoritative.

        Metrics:
            highest_price
            lowest_price
            max_profit_pct
            max_drawdown_pct
            current_move_pct
        """

        try:
            entry_price = float(
                trade.entry_price
            )

            current_price = float(
                current_price
            )

        except (
            TypeError,
            ValueError,
        ):
            return

        if entry_price <= 0 or current_price <= 0:
            return

        # Stable logical identity for this trade.
        # PaperTrade objects are replaced on every price update,
        # so id(trade) is NOT stable and resets V2 metrics.
        entry_time = getattr(trade, "entry_time", None)

        if hasattr(entry_time, "isoformat"):
            entry_time_key = entry_time.isoformat()
        else:
            entry_time_key = str(entry_time)

        key = (
            f"{trade.exchange}|"
            f"{trade.option_token}|"
            f"{entry_time_key}|"
            f"{trade.entry_price}"
        )

        metrics = self._trade_metrics.get(
            key
        )

        if metrics is None:

            metrics = {
                "symbol": trade.option_symbol,
                "entry_price": entry_price,
                "highest_price": entry_price,
                "lowest_price": entry_price,
                "max_profit_pct": 0.0,
                "max_drawdown_pct": 0.0,
            }

            self._trade_metrics[key] = metrics

        metrics["highest_price"] = max(
            metrics["highest_price"],
            current_price,
        )

        metrics["lowest_price"] = min(
            metrics["lowest_price"],
            current_price,
        )

        current_move_pct = (
            (
                current_price
                - entry_price
            )
            / entry_price
        ) * 100.0

        max_profit_pct = (
            (
                metrics["highest_price"]
                - entry_price
            )
            / entry_price
        ) * 100.0

        max_drawdown_pct = (
            (
                metrics["lowest_price"]
                - entry_price
            )
            / entry_price
        ) * 100.0

        metrics["current_move_pct"] = (
            current_move_pct
        )

        metrics["max_profit_pct"] = (
            max_profit_pct
        )

        metrics["max_drawdown_pct"] = (
            max_drawdown_pct
        )

        print(
            "PAPER TRADE METRICS | "
            f"Symbol={trade.option_symbol} | "
            f"Entry={entry_price:.2f} | "
            f"Current={current_price:.2f} | "
            f"High={metrics['highest_price']:.2f} | "
            f"Low={metrics['lowest_price']:.2f} | "
            f"Move={current_move_pct:.2f}% | "
            f"MFE={max_profit_pct:.2f}% | "
            f"MAE={max_drawdown_pct:.2f}%"
        )

        return metrics

    # ========================================================
    # PNL
    # ========================================================

    @staticmethod
    def _calculate_pnl(
        trade: PaperTrade,
        current_price: float,
    ) -> float:

        difference = (
            current_price
            - trade.entry_price
        )

        if trade.signal == SignalType.SELL:

            difference = -difference

        return (
            difference
            * trade.quantity
        )

    # ========================================================
    # MARKET HOURS
    # ========================================================

    @staticmethod
    def _market_open() -> bool:

        now = datetime.now(IST)

        if now.weekday() >= 5:

            return False

        market_start = dt_time(
            9,
            15,
        )

        market_end = dt_time(
            15,
            30,
        )

        current = now.time()

        return (
            market_start
            <= current
            <= market_end
        )

    # ========================================================
    # PERSISTENCE
    # ========================================================

    def _save(self):

        self.DATA_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        def serialize_trade(trade):

            trade_data = asdict(trade)

            trade_data["signal"] = (
                trade.signal.value
            )

            return trade_data

        data = {

            "capital":
                self._portfolio.capital,

            "available_capital":
                self._portfolio.available_capital,

            "realized_pnl":
                self._portfolio.realized_pnl,

            "open_trades": [

                serialize_trade(trade)

                for trade
                in self._portfolio.open_trades
            ],

            "closed_trades": [

                serialize_trade(trade)

                for trade
                in self._portfolio.closed_trades
            ],
        }

        self.DATA_FILE.write_text(

            json.dumps(
                data,
                indent=2,
                default=str,
            ),

            encoding="utf-8",
        )

    # ========================================================
    # LOAD
    # ========================================================

    def _load(self):

        if not self.DATA_FILE.exists():

            return

        try:

            data = json.loads(
                self.DATA_FILE.read_text(
                    encoding="utf-8"
                )
            )

            self._portfolio.capital = float(
                data.get(
                    "capital",
                    self.INITIAL_CAPITAL,
                )
            )

            self._portfolio.available_capital = float(
                data.get(
                    "available_capital",
                    self.INITIAL_CAPITAL,
                )
            )

            self._portfolio.realized_pnl = float(
                data.get(
                    "realized_pnl",
                    0.0,
                )
            )

            def deserialize_signal(value):

                signal_value = str(value)

                if signal_value.startswith(
                    "SignalType."
                ):

                    signal_value = (
                        signal_value.split(
                            ".",
                            1,
                        )[1]
                    )

                return SignalType(
                    signal_value
                )

            #
            # Restore open trades.
            #

            self._portfolio.open_trades = []

            for item in data.get(
                "open_trades",
                [],
            ):

                try:

                    trade = PaperTrade(

                        signal=deserialize_signal(
                            item["signal"]
                        ),

                        option_symbol=item.get(
                            "option_symbol",
                            "",
                        ),

                        option_token=item.get(
                            "option_token",
                            "",
                        ),

                        exchange=item.get(
                            "exchange",
                            "",
                        ),

                        strike=float(
                            item.get(
                                "strike",
                                0.0,
                            )
                            or 0.0
                        ),

                        expiry=item.get(
                            "expiry",
                            "",
                        ),

                        option_type=item.get(
                            "option_type",
                            "",
                        ),

                        entry_price=float(
                            item["entry_price"]
                        ),

                        quantity=int(
                            item["quantity"]
                        ),

                        stop_loss=float(
                            item["stop_loss"]
                        ),

                        target_price=float(
                            item["target_price"]
                        ),

                        status=item.get(
                            "status",
                            "OPEN",
                        ),

                        pnl=float(
                            item.get(
                                "pnl",
                                0.0,
                            )
                        ),

                        current_price=float(
                            item.get(
                                "current_price",
                                0.0,
                            )
                            or 0.0
                        ),

                        entry_time=(
                            datetime.fromisoformat(
                                item["entry_time"]
                            )
                            if item.get("entry_time")
                            else None
                        ),

                        exit_time=(
                            datetime.fromisoformat(
                                item["exit_time"]
                            )
                            if item.get("exit_time")
                            else None
                        ),

                        reason=item.get(
                            "reason",
                            "",
                        ),
                    )

                    self._portfolio.open_trades.append(
                        trade
                    )

                except Exception as exc:

                    print(
                        "Failed to restore open paper trade:",
                        exc,
                    )

            #
            # Restore closed trades.
            #

            self._portfolio.closed_trades = []

            for item in data.get(
                "closed_trades",
                [],
            ):

                try:

                    trade = PaperTrade(

                        signal=deserialize_signal(
                            item["signal"]
                        ),

                        option_symbol=item.get(
                            "option_symbol",
                            "",
                        ),

                        option_token=item.get(
                            "option_token",
                            "",
                        ),

                        exchange=item.get(
                            "exchange",
                            "",
                        ),

                        strike=float(
                            item.get(
                                "strike",
                                0.0,
                            )
                            or 0.0
                        ),

                        expiry=item.get(
                            "expiry",
                            "",
                        ),

                        option_type=item.get(
                            "option_type",
                            "",
                        ),

                        entry_price=float(
                            item["entry_price"]
                        ),

                        quantity=int(
                            item["quantity"]
                        ),

                        stop_loss=float(
                            item["stop_loss"]
                        ),

                        target_price=float(
                            item["target_price"]
                        ),

                        status=item.get(
                            "status",
                            "CLOSED",
                        ),

                        pnl=float(
                            item.get(
                                "pnl",
                                0.0,
                            )
                        ),

                        current_price=float(
                            item.get(
                                "current_price",
                                0.0,
                            )
                            or 0.0
                        ),

                        entry_time=(
                            datetime.fromisoformat(
                                item["entry_time"]
                            )
                            if item.get("entry_time")
                            else None
                        ),

                        exit_time=(
                            datetime.fromisoformat(
                                item["exit_time"]
                            )
                            if item.get("exit_time")
                            else None
                        ),

                        reason=item.get(
                            "reason",
                            "",
                        ),
                    )

                    self._portfolio.closed_trades.append(
                        trade
                    )

                except Exception as exc:

                    print(
                        "Failed to restore closed paper trade:",
                        exc,
                    )

            print(
                "Paper Trading Data Restored | "
                f"Open={len(self._portfolio.open_trades)} | "
                f"Closed={len(self._portfolio.closed_trades)} | "
                f"PnL={self._portfolio.realized_pnl:.2f}"
            )

        except Exception as exc:

            print(
                "Paper Trading Data Load Failed:",
                exc,
            )
