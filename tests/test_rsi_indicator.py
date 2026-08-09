from datetime import datetime, timedelta

from tools.indicators.rsi_indicator import RSIIndicator
from tools.scanner.market_data_models import Candle, MarketData


class TestRSIIndicator:

    def setup_method(self):

        self.market_data = MarketData(
            symbol="SBIN",
            exchange="NSE",
            timeframe="1D",
        )

        start = datetime(2025, 1, 1)

        for i in range(30):

            price = 100.0 + i

            self.market_data.candles.append(
                Candle(
                    timestamp=start + timedelta(days=i),
                    open=price,
                    high=price + 1,
                    low=price - 1,
                    close=price,
                    volume=1000 + i,
                )
            )

    # ---------------------------------------------------------

    def test_constructor(self):

        rsi = RSIIndicator(period=14)

        assert rsi.period == 14

    # ---------------------------------------------------------

    def test_invalid_period(self):

        try:
            RSIIndicator(period=0)
            assert False
        except ValueError:
            assert True

    # ---------------------------------------------------------

    def test_calculate(self):

        rsi = RSIIndicator(period=14)

        values = rsi.calculate(self.market_data)

        assert len(values) > 0

        for value in values:
            assert 0.0 <= value <= 100.0

    # ---------------------------------------------------------

    def test_latest(self):

        rsi = RSIIndicator(period=14)

        value = rsi.latest(self.market_data)

        assert value is not None
        assert 0.0 <= value <= 100.0

    # ---------------------------------------------------------

    def test_not_enough_data(self):

        data = MarketData(
            symbol="ABC",
            exchange="NSE",
            timeframe="1D",
        )

        start = datetime(2025, 1, 1)

        for i in range(5):

            data.candles.append(
                Candle(
                    timestamp=start + timedelta(days=i),
                    open=100,
                    high=101,
                    low=99,
                    close=100,
                    volume=100,
                )
            )

        rsi = RSIIndicator(period=14)

        assert rsi.calculate(data) == []
        assert rsi.latest(data) is None

    # ---------------------------------------------------------

    def test_string(self):

        rsi = RSIIndicator(period=14)

        assert "RSI" in str(rsi)
        assert str(rsi) == repr(rsi)
