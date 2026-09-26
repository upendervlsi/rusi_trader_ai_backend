"""
============================================================

RUSI Trader AI

Dashboard Service

Provides complete dashboard information for Flutter.

============================================================
"""

from datetime import datetime, timezone

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)

from backend.services.market_service import (
    MarketService,
)

from backend.services.recommendation_service import (
    RecommendationService,
)

from backend.services.market_monitor.market_monitor_service import (
    MarketMonitorService,
)

from backend.services.market_pulse_service import (
    MarketPulseService,
)

from backend.services.paper_trading_service import (
    PaperTradingService,
)

from backend.models.dashboard_model import (
    DashboardModel,
    PortfolioSummaryModel,
    TodayPnLModel,
    CurrentTradeModel,
    AITradeSignalModel,
    TodayExecutionModel,
    TradeHistoryModel,
    CurrentMarketSignalModel,
)


class DashboardService:

    """
    Aggregates dashboard information.

    The dashboard is read-only.

    No broker calls are performed here.
    """

    def __init__(self):

        self._market_monitor = (
            MarketMonitorService()
        )

        self._facade = (
            TradingEngineFacade()
        )

        self._market_service = (
            MarketService()
        )

        self._recommendation_service = (
            RecommendationService()
        )

        self._market_pulse_service = (
            MarketPulseService()
        )

        #
        # Persistent paper-trading runtime.
        #
        # Dashboard reads this service only.
        # No trading action is performed here.
        #

        self._paper_trading_service = (
            PaperTradingService()
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _today():

        return datetime.now().date()

    @staticmethod
    def _as_string(value):

        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.isoformat()

        return str(value)

    # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------

    def get_dashboard(self):

        state = (
            self._facade.get_runtime_state()
        )

        market = (
            self._market_service.get_market()
        )

        recommendation = (
            self._recommendation_service
            .get_recommendation()
        )

        summary = (
            state.portfolio_summary
        )

        updated_time = (
            state.updated_time
        )

        #
        # Existing runtime market information.
        #

        markets = (
            self._market_monitor
            .get_market_quotes()
        )

        #
        # Existing market pulse.
        #

        market_pulse = (
            self._market_pulse_service
            .get_market_pulse(
                updated_time
            )
        )

        (
            strongest_market,
            strongest_confidence,
        ) = (
            self._market_pulse_service
            .strongest_market(
                market_pulse
            )
        )

        # =====================================================
        # TODAY'S EXECUTION DATA
        # =====================================================

        #
        # Persistent paper-trading portfolio.
        #
        # This is the authoritative source for today's
        # paper-trading execution results.
        #

        paper_snapshot = (
            self._paper_trading_service
            .dashboard_snapshot()
        )

        paper_open_trades = list(
            paper_snapshot.get(
                "open_trades",
                [],
            )
            or []
        )

        paper_closed_trades = list(
            paper_snapshot.get(
                "closed_trades",
                [],
            )
            or []
        )

        today = self._today()

        today_closed = []

        for trade in paper_closed_trades:

            exit_time = getattr(
                trade,
                "exit_time",
                None,
            )

            if exit_time is None:
                continue

            if hasattr(exit_time, "date"):

                if exit_time.date() == today:
                    today_closed.append(trade)

        #
        # Realized P&L from today's closed
        # paper trades.
        #

        realized_pnl = sum(
            float(
                getattr(
                    trade,
                    "pnl",
                    0.0,
                )
                or 0.0
            )
            for trade in today_closed
        )

        #
        # Current open paper trades.
        #

        open_positions = paper_open_trades

        #
        # Paper-trading unrealized P&L.
        #

        unrealized_pnl = sum(
            (
                float(
                    getattr(
                        trade,
                        "current_price",
                        0.0,
                    )
                    or 0.0
                )
                - float(
                    getattr(
                        trade,
                        "entry_price",
                        0.0,
                    )
                    or 0.0
                )
            )
            * int(
                getattr(
                    trade,
                    "quantity",
                    0,
                )
                or 0
            )
            for trade in open_positions
        )

        net_pnl = (
            realized_pnl
            + unrealized_pnl
        )

        wins = sum(
            1
            for trade in today_closed
            if float(
                getattr(
                    trade,
                    "pnl",
                    0.0,
                )
                or 0.0
            ) > 0
        )

        losses = sum(
            1
            for trade in today_closed
            if float(
                getattr(
                    trade,
                    "pnl",
                    0.0,
                )
                or 0.0
            ) < 0
        )

        trades = len(today_closed)

        win_rate = (
            (wins / trades) * 100.0
            if trades > 0
            else 0.0
        )

        # =====================================================
        # CURRENT TRADE
        # =====================================================

        current_trade = None

        if open_positions:

            trade = open_positions[-1]

            trade_current_price = float(
                getattr(
                    trade,
                    "current_price",
                    getattr(
                        trade,
                        "entry_price",
                        0.0,
                    ),
                )
                or 0.0
            )

            trade_entry_price = float(
                getattr(
                    trade,
                    "entry_price",
                    0.0,
                )
                or 0.0
            )

            trade_quantity = int(
                getattr(
                    trade,
                    "quantity",
                    0,
                )
                or 0
            )

            trade_pnl = (
                trade_current_price
                - trade_entry_price
            ) * trade_quantity

            current_trade = CurrentTradeModel(

                position_id=(
                    f"PAPER-{id(trade)}"
                ),

                symbol=(
                    getattr(
                        trade,
                        "option_symbol",
                        "",
                    )
                    or ""
                ),

                exchange=(
                    getattr(
                        trade,
                        "exchange",
                        "NFO",
                    )
                    or "NFO"
                ),

                transaction_type="BUY",

                quantity=(
                    trade_quantity
                ),

                entry_price=(
                    trade_entry_price
                ),

                current_price=(
                    trade_current_price
                ),

                current_pnl=(
                    trade_pnl
                ),

                stop_loss=(
                    float(
                        getattr(
                            trade,
                            "stop_loss",
                            0.0,
                        )
                        or 0.0
                    )
                ),

                target_price=(
                    float(
                        getattr(
                            trade,
                            "target_price",
                            0.0,
                        )
                        or 0.0
                    )
                ),

                protection="INACTIVE",

                status=(
                    getattr(
                        trade,
                        "status",
                        "OPEN",
                    )
                    or "OPEN"
                ),

                entry_time=(
                    self._as_string(
                        getattr(
                            trade,
                            "entry_time",
                            None,
                        )
                    )
                ),
            )

        # =====================================================
        # AI TRADE SIGNAL
        # =====================================================

        direction = (
            recommendation.recommendation
            if recommendation
            else None
        )

        signal_status = (
            "WORKING"
            if direction in ("BUY", "SELL")
            else "WAITING"
        )

        option = (
            recommendation.option_type
            if recommendation
            else None
        )

        option_symbol = (
            recommendation.option_symbol
            if recommendation
            else None
        )

        ai_trade_signal = AITradeSignalModel(

            direction=direction,

            confidence=(
                recommendation.confidence
                if recommendation
                else None
            ),

            score=(
                recommendation.score
                if recommendation
                else None
            ),

            option=option,

            option_symbol=option_symbol,

            signal_status=signal_status,
        )

        # =====================================================
        # TRADE HISTORY
        # =====================================================

        trade_history = []

        for trade in reversed(today_closed):

            symbol = (
                getattr(
                    trade,
                    "option_symbol",
                    "",
                )
                or ""
            )

            option_type = (
                getattr(
                    trade,
                    "option_type",
                    "",
                )
                or ""
            )

            if not option_type:

                if symbol.endswith("CE"):
                    option_type = "CE"

                elif symbol.endswith("PE"):
                    option_type = "PE"

            trade_history.append(
                TradeHistoryModel(

                    position_id=(
                        f"PAPER-{id(trade)}"
                    ),

                    symbol=symbol,

                    exchange=(
                        getattr(
                            trade,
                            "exchange",
                            "NFO",
                        )
                        or "NFO"
                    ),

                    option_type=option_type,

                    transaction_type="BUY",

                    quantity=int(
                        getattr(
                            trade,
                            "quantity",
                            0,
                        )
                        or 0
                    ),

                    entry_price=float(
                        getattr(
                            trade,
                            "entry_price",
                            0.0,
                        )
                        or 0.0
                    ),

                    exit_price=float(
                        getattr(
                            trade,
                            "current_price",
                            0.0,
                        )
                        or 0.0
                    ),

                    pnl=float(
                        getattr(
                            trade,
                            "pnl",
                            0.0,
                        )
                        or 0.0
                    ),

                    exit_reason=(
                        getattr(
                            trade,
                            "status",
                            "",
                        )
                        or ""
                    ),

                    entry_time=(
                        self._as_string(
                            getattr(
                                trade,
                                "entry_time",
                                None,
                            )
                        )
                    ),

                    exit_time=(
                        self._as_string(
                            getattr(
                                trade,
                                "exit_time",
                                None,
                            )
                        )
                    ),
                )
            )

        # =====================================================
        # CURRENT MARKET SIGNAL
        # =====================================================

        current_market_signal = CurrentMarketSignalModel(

            symbol="NIFTY1SEP2026",

            display_name="NIFTY 1 SEP 2026",

            signal=direction,

            confidence=(
                recommendation.confidence
                if recommendation
                else None
            ),

            score=(
                recommendation.score
                if recommendation
                else None
            ),

            last_price=(
                state.live_price
            ),

            updated_time=(
                updated_time
            ),
        )

        # =====================================================
        # FINAL DASHBOARD
        # =====================================================

        return DashboardModel(

            market_status=(
                market.market_status
            ),

            updated_time=(
                updated_time
            ),

            markets=markets,

            market_pulse=market_pulse,

            strongest_market=(
                strongest_market
            ),

            strongest_confidence=(
                strongest_confidence
            ),

            recommendation=(
                recommendation.recommendation
            ),

            confidence=(
                recommendation.confidence
            ),

            portfolio=PortfolioSummaryModel(

                open_positions=(
                    summary.open_positions
                    if summary
                    else 0
                ),

                invested_amount=(
                    summary.invested_amount
                    if summary
                    else 0.0
                ),

                market_value=(
                    summary.market_value
                    if summary
                    else 0.0
                ),

                unrealized_pnl=(
                    summary.unrealized_pnl
                    if summary
                    else 0.0
                ),
            ),

            today_pnl=TodayPnLModel(

                realized_pnl=(
                    realized_pnl
                ),

                unrealized_pnl=(
                    unrealized_pnl
                ),

                net_pnl=(
                    net_pnl
                ),
            ),

            current_trade=current_trade,

            ai_trade_signal=(
                ai_trade_signal
            ),

            today_execution=TodayExecutionModel(

                trades=trades,

                wins=wins,

                losses=losses,

                win_rate=win_rate,
            ),

            trade_history=trade_history,

            current_market_signal=(
                current_market_signal
            ),
        )
