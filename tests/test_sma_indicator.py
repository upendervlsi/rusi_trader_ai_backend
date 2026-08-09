from datetime import datetime, timedelta

from tools.indicators.sma_indicator import SMAIndicator
from tools.scanner.market_data_models import Candle, MarketData


class TestSMAIndicator:

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

        sma = SMAIndicator(period=20)

        assert sma.period == 20

    # ---------------------------------------------------------

    def test_invalid_period(self):

        try:
            SMAIndicator(period=0)
            assert False
        except ValueError:
            assert True

    # ---------------------------------------------------------

    def test_calculate(self):

        sma = SMAIndicator(period=20)

        values = sma.calculate(self.market_data)

        assert len(values) == 11

    # ---------------------------------------------------------

    def test_latest(self):

        sma = SMAIndicator(period=20)

        value = sma.latest(self.market_data)

        assert value is not None

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

        sma = SMAIndicator(period=20)

        assert sma.calculate(data) == []
        assert sma.latest(data) is None

    # ---------------------------------------------------------

    def test_string(self):

        sma = SMAIndicator(period=20)

        assert "SMA" in str(sma)
        assert str(sma) == repr(sma)
