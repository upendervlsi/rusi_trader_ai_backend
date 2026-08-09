from datetime import datetime, timedelta

from tools.indicators.indicator_engine import IndicatorEngine
from tools.scanner.market_data_models import Candle, MarketData


class TestIndicatorEngine:

    def setup_method(self):

        self.engine = IndicatorEngine()

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

    def test_compute(self):

        results = self.engine.compute(self.market_data)

        assert "ema20" in results
        assert "sma20" in results
        assert "rsi14" in results
        assert "macd" in results
        assert "atr14" in results
        assert "adx14" in results
        assert "vwap" in results

        assert results["ema20"] is not None
        assert results["sma20"] is not None
        assert results["rsi14"] is not None
        assert results["macd"] is not None
        assert results["atr14"] is not None
        assert results["adx14"] is not None
        assert results["vwap"] is not None
    # ---------------------------------------------------------

    def test_cache(self):

        self.engine.compute(self.market_data)

        assert self.engine.has_cached("ema20")
        assert self.engine.has_cached("sma20")
        assert self.engine.has_cached("rsi14")
        assert self.engine.has_cached("macd")
        assert self.engine.has_cached("atr14")
        assert self.engine.has_cached("adx14")

        assert self.engine.has_cached("vwap")

        value = self.engine.get_cached("vwap")

        assert value is not None

    # ---------------------------------------------------------

    def test_clear_cache(self):

        self.engine.compute(self.market_data)

        self.engine.clear_cache()

        assert not self.engine.has_cached("ema20")
        assert not self.engine.has_cached("sma20")
        assert not self.engine.has_cached("rsi14")
        assert not self.engine.has_cached("macd")
        assert not self.engine.has_cached("atr14")
        assert not self.engine.has_cached("adx14")
        assert not self.engine.has_cached("vwap")

    # ---------------------------------------------------------

    def test_manual_cache(self):

        self.engine.cache("dummy", 123)

        assert self.engine.has_cached("dummy")
        assert self.engine.get_cached("dummy") == 123
