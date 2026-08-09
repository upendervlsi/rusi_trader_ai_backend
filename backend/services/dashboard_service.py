"""
============================================================

RUSI Trader AI

Dashboard Service

Provides complete dashboard information for Flutter.

Author : RUSI Trader AI

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
from backend.models.dashboard_model import (
    DashboardModel,
    PortfolioSummaryModel,
)

from backend.models.market_quote_model import (
    MarketQuoteModel,
)
from backend.services.market_monitor.market_monitor_service import (
    MarketMonitorService,
)

class DashboardService:

    """
    Dashboard Service

    Aggregates all dashboard information.

    This service never performs calculations.

    It simply collects runtime information from the
    existing services.
    """

    def __init__(self):
        self._market_monitor = (
            MarketMonitorService()
        )
        self._facade = TradingEngineFacade()

        self._market_service = MarketService()

        self._recommendation_service = (
            RecommendationService()
        )

    def get_dashboard(self):

        state = self._facade.get_runtime_state()

        market = self._market_service.get_market()

        recommendation = (
            self._recommendation_service
            .get_recommendation()
        )

        summary = state.portfolio_summary

        return DashboardModel(

            market_status=market.market_status,

            updated_time=state.updated_time,

            markets=self._market_monitor.get_market_quotes(),

            recommendation=recommendation.recommendation,

            confidence=recommendation.confidence,

            portfolio=PortfolioSummaryModel(

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
