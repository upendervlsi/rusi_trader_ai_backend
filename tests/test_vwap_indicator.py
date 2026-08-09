from datetime import datetime, timedelta

from tools.indicators.vwap_indicator import VWAPIndicator
from tools.scanner.market_data_models import Candle, MarketData


class TestVWAPIndicator:

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
                    high=price + 2,
                    low=price - 2,
                    close=price + 1,
                    volume=1000 + i,
                )
            )

    # -------------------------------------------------

    def test_calculate(self):

        indicator = VWAPIndicator()

        values = indicator.calculate(self.market_data)

        assert len(values) == len(
            self.market_data.candles
        )

        for value in values:
            assert value > 0

    # -------------------------------------------------

    def test_latest(self):

        indicator = VWAPIndicator()

        value = indicator.latest(self.market_data)

        assert value is not None
        assert value > 0

    # -------------------------------------------------

    def test_empty_data(self):

        data = MarketData(
            symbol="ABC",
            exchange="NSE",
            timeframe="1D",
        )

        indicator = VWAPIndicator()

        assert indicator.calculate(data) == []
        assert indicator.latest(data) is None

    # -------------------------------------------------

    def test_string(self):

        indicator = VWAPIndicator()

        assert "VWAP" in str(indicator)
        assert str(indicator) == repr(indicator)
