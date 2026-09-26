"""
========================================================================

RUSI Trader AI

Paper Portfolio Manager

========================================================================
"""

from __future__ import annotations

from intelligence.paper_trading.paper_portfolio import (
    PaperPortfolio,
)

from intelligence.paper_trading.paper_trade import (
    PaperTrade,
)

from intelligence.paper_trading.trade_status import (
    TradeStatus,
)

from intelligence.signals.signal_type import (
    SignalType,
)


class PaperPortfolioManager:

    def add_trade(
        self,
        portfolio: PaperPortfolio,
        trade: PaperTrade,
    ) -> None:

        portfolio.open_trades.append(
            trade
        )

    def update_trade(
        self,
        portfolio: PaperPortfolio,
        index: int,
        current_price: float,
    ) -> None:

        trade = (
            portfolio.open_trades[index]
        )

        difference = (
            current_price -
            trade.entry_price
        )

        #
        # SELL profits when price falls.
        #
        if trade.signal == SignalType.SELL:

            difference = -difference

        pnl = (
            difference *
            trade.quantity
        )

        status = (
            TradeStatus.OPEN.value
        )

        #
        # BUY exit rules
        #
        if trade.signal == SignalType.BUY:

            if (
                current_price >=
                trade.target_price
            ):

                status = (
                    TradeStatus.TARGET.value
                )

            elif (
                current_price <=
                trade.stop_loss
            ):

                status = (
                    TradeStatus.STOP_LOSS.value
                )

        #
        # SELL exit rules
        #
        elif trade.signal == SignalType.SELL:

            if (
                current_price <=
                trade.target_price
            ):

                status = (
                    TradeStatus.TARGET.value
                )

            elif (
                current_price >=
                trade.stop_loss
            ):

                status = (
                    TradeStatus.STOP_LOSS.value
                )

        #
        # Close trade.
        #
        if (
            status !=
            TradeStatus.OPEN.value
        ):

            closed_trade = PaperTrade(

                signal=trade.signal,

                entry_price=trade.entry_price,

                quantity=trade.quantity,

                stop_loss=trade.stop_loss,

                target_price=trade.target_price,

                status=status,

                pnl=pnl,

                reason=trade.reason,
            )

            portfolio.closed_trades.append(
                closed_trade
            )

            portfolio.realized_pnl += pnl

            del portfolio.open_trades[
                index
            ]
