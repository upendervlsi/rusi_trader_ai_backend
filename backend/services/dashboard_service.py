"""
============================================================

RUSI Trader AI

Dashboard Service

Provides complete dashboard information for Flutter.

============================================================
"""

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

from backend.models.dashboard_model import (
    DashboardModel,
    PortfolioSummaryModel,
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
        # New seven-market dashboard view.
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

        return DashboardModel(

            market_status=
                market.market_status,

            updated_time=
                updated_time,

            markets=
                markets,

            market_pulse=
                market_pulse,

            strongest_market=
                strongest_market,

            strongest_confidence=
                strongest_confidence,

            recommendation=
                recommendation.recommendation,

            confidence=
                recommendation.confidence,

            portfolio=
                PortfolioSummaryModel(

                    open_positions=
                        summary.open_positions
                        if summary
                        else 0,

                    invested_amount=
                        summary.invested_amount
                        if summary
                        else 0.0,

                    market_value=
                        summary.market_value
                        if summary
                        else 0.0,

                    unrealized_pnl=
                        summary.unrealized_pnl
                        if summary
                        else 0.0,
                ),
        )
