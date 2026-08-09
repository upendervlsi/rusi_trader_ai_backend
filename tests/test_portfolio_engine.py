"""
============================================================
RUSI Trader AI

V1.0

Portfolio Engine Unit Tests
============================================================
"""

import pytest

from tools.portfolio.portfolio_engine import PortfolioEngine
from tools.portfolio.portfolio_models import Position


class TestPortfolioEngine:

    def setup_method(self):

        self.engine = PortfolioEngine(
            initial_cash=100000.0,
        )

    # ---------------------------------------------------------

    def _position(self):

        return Position(
            symbol="INFY",
            quantity=100,
            entry_price=100.0,
            current_price=110.0,
            stop_loss=95.0,
            target_price=130.0,
        )

    # ---------------------------------------------------------

    def test_constructor(self):

        assert self.engine.state.cash == 100000.0
        assert len(self.engine.state.positions) == 0

    # ---------------------------------------------------------

    def test_open_position(self):

        self.engine.open_position(
            self._position()
        )

        assert self.engine.state.cash == 90000.0
        assert self.engine.get_position("INFY") is not None

    # ---------------------------------------------------------

    def test_close_position(self):

        self.engine.open_position(
            self._position()
        )

        self.engine.close_position("INFY")

        assert self.engine.state.cash == 101000.0
        assert self.engine.get_position("INFY") is None

    # ---------------------------------------------------------

    def test_summary(self):

        self.engine.open_position(
            self._position()
        )

        summary = self.engine.portfolio_summary()

        assert summary.available_cash == 90000.0
        assert summary.invested_capital == 10000.0
        assert summary.total_market_value == 11000.0
        assert summary.unrealized_pnl == 1000.0
        assert summary.open_positions == 1

    # ---------------------------------------------------------

    def test_insufficient_cash(self):

        engine = PortfolioEngine(
            initial_cash=1000.0,
        )

        with pytest.raises(ValueError):

            engine.open_position(
                self._position()
            )

    # ---------------------------------------------------------

    def test_string(self):

        assert "PortfolioEngine" in str(self.engine)
        assert "PortfolioEngine" in repr(self.engine)
