"""
============================================================
RUSI Trader AI

V1.0

Portfolio Model Unit Tests
============================================================
"""

from tools.portfolio.portfolio_models import (
    Position,
    PortfolioState,
    PortfolioSummary,
)


class TestPortfolioModels:

    def test_position_properties(self):

        position = Position(
            symbol="INFY",
            quantity=10,
            entry_price=100.0,
            current_price=120.0,
            stop_loss=95.0,
            target_price=140.0,
        )

        assert position.market_value == 1200.0
        assert position.cost_basis == 1000.0
        assert position.unrealized_pnl == 200.0

    # ---------------------------------------------------------

    def test_add_position(self):

        portfolio = PortfolioState(
            cash=100000.0,
        )

        position = Position(
            symbol="TCS",
            quantity=5,
            entry_price=200.0,
            current_price=210.0,
            stop_loss=190.0,
            target_price=250.0,
        )

        portfolio.add_position(position)

        assert portfolio.has_position("TCS")

    # ---------------------------------------------------------

    def test_remove_position(self):

        portfolio = PortfolioState(
            cash=100000.0,
        )

        position = Position(
            symbol="SBIN",
            quantity=10,
            entry_price=500.0,
            current_price=510.0,
            stop_loss=480.0,
            target_price=560.0,
        )

        portfolio.add_position(position)

        portfolio.remove_position("SBIN")

        assert not portfolio.has_position("SBIN")

    # ---------------------------------------------------------

    def test_summary(self):

        summary = PortfolioSummary(
            available_cash=50000.0,
            invested_capital=40000.0,
            total_market_value=43000.0,
            unrealized_pnl=3000.0,
            realized_pnl=1500.0,
            open_positions=2,
        )

        assert summary.available_cash == 50000.0
        assert summary.open_positions == 2

    # ---------------------------------------------------------

    def test_string(self):

        portfolio = PortfolioState(
            cash=100000.0,
        )

        assert "PortfolioState" in str(portfolio)
        assert "PortfolioState" in repr(portfolio)
