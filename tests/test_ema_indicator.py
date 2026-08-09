from datetime import datetime, timedelta

from tools.indicators.ema_indicator import EMAIndicator
from tools.scanner.market_data_models import Candle, MarketData


class TestEMAIndicator:

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

        ema = EMAIndicator(period=20)

        assert ema.period == 20

    # ---------------------------------------------------------

    def test_invalid_period(self):

        try:
            EMAIndicator(period=0)
            assert False
        except ValueError:
            assert True

    # ---------------------------------------------------------

    def test_calculate(self):

        ema = EMAIndicator(period=20)

        values = ema.calculate(self.market_data)

        assert len(values) == 11

    # ---------------------------------------------------------

    def test_latest(self):

        ema = EMAIndicator(period=20)

        value = ema.latest(self.market_data)

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

        ema = EMAIndicator(period=20)

        assert ema.calculate(data) == []
        assert ema.latest(data) is None

    # ---------------------------------------------------------

    def test_string(self):

        ema = EMAIndicator(period=20)

        assert "EMA" in str(ema)
        assert str(ema) == repr(ema)
