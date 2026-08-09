from datetime import datetime, timedelta

from tools.indicators.adx_indicator import ADXIndicator
from tools.scanner.market_data_models import Candle, MarketData


class TestADXIndicator:

    def setup_method(self):

        self.market_data = MarketData(
            symbol="SBIN",
            exchange="NSE",
            timeframe="1D",
        )

        start = datetime(2025, 1, 1)

        for i in range(40):

            price = 100.0 + i

            self.market_data.candles.append(
                Candle(
                    timestamp=start + timedelta(days=i),
                    open=price,
                    high=price + 2.0,
                    low=price - 2.0,
                    close=price + 1.0,
                    volume=1000 + i,
                )
            )

    # ---------------------------------------------------------

    def test_constructor(self):

        adx = ADXIndicator(period=14)

        assert adx.period == 14

    # ---------------------------------------------------------

    def test_invalid_period(self):

        try:
            ADXIndicator(period=0)
            assert False
        except ValueError:
            assert True

    # ---------------------------------------------------------

    def test_calculate(self):

        adx = ADXIndicator(period=14)

        values = adx.calculate(self.market_data)

        assert len(values) > 0

        for value in values:
            assert value >= 0.0
            assert value <= 100.0

    # ---------------------------------------------------------

    def test_latest(self):

        adx = ADXIndicator(period=14)

        value = adx.latest(self.market_data)

        assert value is not None
        assert value >= 0.0
        assert value <= 100.0

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
                    high=102,
                    low=98,
                    close=101,
                    volume=100,
                )
            )

        adx = ADXIndicator(period=14)

        assert adx.calculate(data) == []
        assert adx.latest(data) is None

    # ---------------------------------------------------------

    def test_string(self):

        adx = ADXIndicator(period=14)

        assert "ADX" in str(adx)
        assert str(adx) == repr(adx)
