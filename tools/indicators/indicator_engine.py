"""
============================================================
RUSI Trader AI

Indicator Engine

Central registry for all technical indicators.
============================================================
"""

from __future__ import annotations

from tools.scanner.market_data_models import MarketData
from tools.indicators.ema_indicator import EMAIndicator
from tools.indicators.sma_indicator import SMAIndicator
from tools.indicators.rsi_indicator import RSIIndicator
from tools.indicators.macd_indicator import MACDIndicator
from tools.indicators.atr_indicator import ATRIndicator
from tools.indicators.adx_indicator import ADXIndicator
from tools.indicators.vwap_indicator import VWAPIndicator

class IndicatorEngine:
    """
    Central engine responsible for computing
    technical indicators.
    """

    def __init__(self) -> None:

        self._cache: dict[str, object] = {}


        self._ema = EMAIndicator(period=20)
        self._sma = SMAIndicator(period=20)
        self._rsi = RSIIndicator(period=14)
        self._macd = MACDIndicator()
        self._atr = ATRIndicator(period=14)
        self._adx = ADXIndicator(period=14)
        self._vwap = VWAPIndicator()
    # ---------------------------------------------------------

    def clear_cache(self) -> None:
        """
        Clear all cached indicator values.
        """

        self._cache.clear()

    # ---------------------------------------------------------

    def has_cached(
        self,
        name: str,
    ) -> bool:
        """
        Check whether an indicator result exists.
        """

        return name in self._cache

    # ---------------------------------------------------------

    def get_cached(
        self,
        name: str,
    ) -> object | None:
        """
        Retrieve a cached indicator.
        """

        return self._cache.get(name)

    # ---------------------------------------------------------

    def cache(
        self,
        name: str,
        value: object,
    ) -> None:
        """
        Store an indicator result.
        """

        self._cache[name] = value

    # ---------------------------------------------------------

    def compute(
        self,
        market_data: MarketData,
    ) -> dict[str, object]:

        self.clear_cache()

        results: dict[str, object] = {}

        ema20 = self._ema.latest(market_data)
        sma20 = self._sma.latest(market_data)
        rsi14 = self._rsi.latest(market_data)
        macd = self._macd.latest(market_data)
        atr14 = self._atr.latest(market_data)
        adx14 = self._adx.latest(market_data)
        vwap = self._vwap.latest(market_data)

        results["ema20"] = ema20
        results["sma20"] = sma20
        results["rsi14"] = rsi14
        results["macd"] = macd
        results["atr14"] = atr14
        results["adx14"] = adx14
        results["vwap"] = vwap

        self.cache("ema20", ema20)
        self.cache("sma20", sma20)
        self.cache("rsi14", rsi14)
        self.cache("macd", macd)
        self.cache("atr14", atr14)
        self.cache("adx14", adx14)
        self.cache("vwap", vwap)

        return results
