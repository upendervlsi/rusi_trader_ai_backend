"""
============================================================

Portfolio Service

============================================================
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from backend.models.portfolio_model import (
    PortfolioModel,
)

from backend.services.paper_trading_service import (
    PaperTradingService,
)


IST = ZoneInfo("Asia/Kolkata")


class PortfolioService:

    def __init__(self):

        self._paper_trading_service = (
            PaperTradingService()
        )

    def get_portfolio(self):

        #
        # RUSI V1:
        #
        # The paper-trading service is the authoritative
        # source for paper positions and their live valuation.
        #
        snapshot = (
            self._paper_trading_service
            .dashboard_snapshot()
        )

        open_trades = list(
            snapshot.get(
                "open_trades",
                [],
            )
            or []
        )

        updated_time = datetime.now(
            IST
        ).isoformat()

        if not open_trades:

            return PortfolioModel(

                open_positions=0,

                invested_amount=0.0,

                market_value=0.0,

                unrealized_pnl=0.0,

                updated_time=updated_time,

            )

        invested_amount = 0.0
        market_value = 0.0
        unrealized_pnl = 0.0

        for trade in open_trades:

            entry_price = float(
                getattr(
                    trade,
                    "entry_price",
                    0.0,
                )
                or 0.0
            )

            current_price = float(
                getattr(
                    trade,
                    "current_price",
                    0.0,
                )
                or 0.0
            )

            quantity = int(
                getattr(
                    trade,
                    "quantity",
                    0,
                )
                or 0
            )

            invested_amount += (
                entry_price * quantity
            )

            market_value += (
                current_price * quantity
            )

            unrealized_pnl += (
                current_price
                - entry_price
            ) * quantity

        return PortfolioModel(

            open_positions=len(
                open_trades
            ),

            invested_amount=(
                invested_amount
            ),

            market_value=(
                market_value
            ),

            unrealized_pnl=(
                unrealized_pnl
            ),

            updated_time=updated_time,

        )
