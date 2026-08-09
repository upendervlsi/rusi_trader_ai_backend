"""
============================================================
RUSI Trader AI

Unit Tests

SuperTrend Indicator
============================================================
"""

import pytest

from tools.indicators.supertrend_indicator import SuperTrendIndicator
from tools.scanner.market_data_models import Candle
from tools.scanner.market_data_models import MarketData


class TestSuperTrendIndicator:

    def setup_method(self):

        candles = []

        price = 100.0

        for _ in range(40):

            candles.append(
                Candle(
                    timestamp="2026-01-01",
                    open=price,
                    high=price + 2.0,
                    low=price - 2.0,
                    close=price + 1.0,
                    volume=1000,
                )
            )

            price += 1.0

        self.market_data = MarketData(
            symbol="TEST",
            exchange="NSE",
            timeframe="1D",
            candles=candles,
        )

    # ---------------------------------------------------------

    def test_constructor(self):

        indicator = SuperTrendIndicator()

        assert indicator.period == 10
        assert indicator.multiplier == 3.0

    # ---------------------------------------------------------

    def test_invalid_period(self):

        with pytest.raises(ValueError):
            SuperTrendIndicator(period=0)

    # ---------------------------------------------------------

    def test_invalid_multiplier(self):

        with pytest.raises(ValueError):
            SuperTrendIndicator(multiplier=0)

    # ---------------------------------------------------------

    def test_calculate(self):

        indicator = SuperTrendIndicator()

        values = indicator.calculate(self.market_data)

        assert len(values) > 0

        latest = values[-1]

        assert "value" in latest
        assert "trend" in latest

        assert latest["trend"] in ("UP", "DOWN")

    # ---------------------------------------------------------

    def test_latest(self):

        indicator = SuperTrendIndicator()

        latest = indicator.latest(self.market_data)

        assert latest is not None

        assert "value" in latest
        assert "trend" in latest

    # ---------------------------------------------------------

    def test_not_enough_data(self):

        market = MarketData(
            symbol="TEST",
            exchange="NSE",
            timeframe="1D",
            candles=[],
        )

        indicator = SuperTrendIndicator()

        assert indicator.latest(market) is None

    # ---------------------------------------------------------

    def test_string(self):

        indicator = SuperTrendIndicator()

        assert "SuperTrend" in str(indicator)
        assert "SuperTrend" in repr(indicator)
