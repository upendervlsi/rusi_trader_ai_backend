from datetime import datetime, timedelta

from tools.indicators.macd_indicator import MACDIndicator
from tools.scanner.market_data_models import Candle, MarketData


class TestMACDIndicator:

    def setup_method(self):

        self.market_data = MarketData(
            symbol="SBIN",
            exchange="NSE",
            timeframe="1D",
        )

        start = datetime(2025, 1, 1)

        for i in range(80):

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

        macd = MACDIndicator()

        assert macd.fast_period == 12
        assert macd.slow_period == 26
        assert macd.signal_period == 9

    # ---------------------------------------------------------

    def test_invalid_periods(self):

        try:
            MACDIndicator(fast_period=0)
            assert False
        except ValueError:
            assert True

        try:
            MACDIndicator(slow_period=0)
            assert False
        except ValueError:
            assert True

        try:
            MACDIndicator(signal_period=0)
            assert False
        except ValueError:
            assert True

    # ---------------------------------------------------------

    def test_fast_less_than_slow(self):

        try:
            MACDIndicator(
                fast_period=30,
                slow_period=20,
            )
            assert False
        except ValueError:
            assert True

    # ---------------------------------------------------------

    def test_calculate(self):

        macd = MACDIndicator()

        result = macd.calculate(self.market_data)

        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result

        assert len(result["macd"]) > 0
        assert len(result["signal"]) > 0
        assert len(result["histogram"]) > 0

    # ---------------------------------------------------------

    def test_latest(self):

        macd = MACDIndicator()

        values = macd.latest(self.market_data)

        assert values["macd"] is not None
        assert values["signal"] is not None
        assert values["histogram"] is not None

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

        macd = MACDIndicator()

        values = macd.latest(data)

        assert values["macd"] is None
        assert values["signal"] is None
        assert values["histogram"] is None

    # ---------------------------------------------------------

    def test_string(self):

        macd = MACDIndicator()

        assert "MACD" in str(macd)
        assert str(macd) == repr(macd)
