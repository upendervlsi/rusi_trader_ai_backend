"""
============================================================

Portfolio Manager

============================================================
"""

from common.logger import get_logger

from execution.portfolio.portfolio import Portfolio
from execution.portfolio.portfolio_summary import PortfolioSummary
from execution.position_manager.position_registry import PositionRegistry

logger = get_logger("RUSI")


class PortfolioManager:

    def __init__(self, registry: PositionRegistry):

        self._registry = registry

    def build_portfolio(self) -> Portfolio:

        portfolio = Portfolio()

        for position in self._registry.open_positions():

            portfolio.positions.append(position)

            portfolio.invested_amount += (
                position.entry_price * position.quantity
            )

            portfolio.market_value += (
                position.current_price * position.quantity
            )

            portfolio.unrealized_pnl += (
                position.unrealized_pnl
            )

            portfolio.realized_pnl += (
                position.realized_pnl
            )

        return portfolio

    def summary(self) -> PortfolioSummary:

        portfolio = self.build_portfolio()

        return PortfolioSummary(

            total_positions=len(portfolio.positions),

            open_positions=len(portfolio.positions),

            invested_amount=portfolio.invested_amount,

            market_value=portfolio.market_value,

            unrealized_pnl=portfolio.unrealized_pnl,

            realized_pnl=portfolio.realized_pnl,

        )
