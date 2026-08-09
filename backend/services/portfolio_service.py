"""
============================================================

Portfolio Service

============================================================
"""

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)

from backend.models.portfolio_model import (
    PortfolioModel,
)


class PortfolioService:

    def __init__(self):

        self._facade = TradingEngineFacade()

    def get_portfolio(self):

        state = self._facade.get_runtime_state()

        portfolio = state.portfolio

        if portfolio is None:

            return PortfolioModel(

                open_positions=0,

                invested_amount=0.0,

                market_value=0.0,

                unrealized_pnl=0.0,

                updated_time=state.updated_time,

            )

        return PortfolioModel(

            open_positions=len(portfolio.positions),

            invested_amount=portfolio.invested_amount,

            market_value=portfolio.market_value,

            unrealized_pnl=portfolio.unrealized_pnl,

            updated_time=state.updated_time,

        )
