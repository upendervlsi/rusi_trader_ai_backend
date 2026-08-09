"""
============================================================
RUSI Trader AI

Indicator Manager

Central manager for technical indicator calculation.

All indicators are calculated from the authoritative
snapshot.candles dataset.

============================================================
"""

from indicators.ema_indicator import EMAIndicator
from indicators.sma_indicator import SMAIndicator

from tools.indicators.rsi_indicator import RSIIndicator
from tools.indicators.macd_indicator import MACDIndicator
from tools.indicators.adx_indicator import ADXIndicator
from tools.indicators.atr_indicator import ATRIndicator

from tools.scanner.market_data_models import MarketData


class IndicatorManager:

    def __init__(self):

        # -----------------------------------------------------
        # Moving averages
        # -----------------------------------------------------

        self._ema = EMAIndicator()
        self._sma = SMAIndicator()

        # -----------------------------------------------------
        # Momentum indicators
        # -----------------------------------------------------

        self._rsi = RSIIndicator(period=14)

        self._macd = MACDIndicator(
            fast_period=12,
            slow_period=26,
            signal_period=9,
        )

        self._adx = ADXIndicator(
            period=14,
        )

        self._atr = ATRIndicator(
            period=14,
        )

    # ---------------------------------------------------------
    # Populate Indicator Snapshot
    # ---------------------------------------------------------

    def populate_snapshot(self, snapshot):

        candles = snapshot.candles

        # -----------------------------------------------------
        # Existing candle container expects MarketData.
        #
        # Build a technology-independent MarketData object
        # from the authoritative runtime candles.
        # -----------------------------------------------------

        market_data = MarketData(
            symbol=getattr(
                snapshot,
                "symbol",
                "",
            ),
            exchange=getattr(
                snapshot,
                "exchange",
                "",
            ),
            timeframe=getattr(
                snapshot,
                "timeframe",
                "",
            ),
            candles=candles,
        )

        # -----------------------------------------------------
        # Moving Averages
        # -----------------------------------------------------

        snapshot.indicators.sma20 = (
            self._sma.calculate(
                candles,
                20,
            )
        )

        snapshot.indicators.sma50 = (
            self._sma.calculate(
                candles,
                50,
            )
        )

        snapshot.indicators.sma200 = (
            self._sma.calculate(
                candles,
                200,
            )
        )

        snapshot.indicators.ema20 = (
            self._ema.calculate(
                candles,
                20,
            )
        )

        snapshot.indicators.ema50 = (
            self._ema.calculate(
                candles,
                50,
            )
        )

        snapshot.indicators.ema200 = (
            self._ema.calculate(
                candles,
                200,
            )
        )

        # -----------------------------------------------------
        # RSI 14
        # -----------------------------------------------------

        snapshot.indicators.rsi14 = (
            self._rsi.latest(
                market_data
            )
        )

        # -----------------------------------------------------
        # MACD 12 / 26 / 9
        # -----------------------------------------------------

        macd_result = (
            self._macd.latest(
                market_data
            )
        )

        snapshot.indicators.macd = (
            macd_result.get("macd")
        )

        snapshot.indicators.signal_line = (
            macd_result.get("signal")
        )

        snapshot.indicators.histogram = (
            macd_result.get("histogram")
        )

        # -----------------------------------------------------
        # ADX 14
        # -----------------------------------------------------

        snapshot.indicators.adx14 = (
            self._adx.latest(
                market_data
            )
        )

        # -----------------------------------------------------
        # ATR 14
        # -----------------------------------------------------

        snapshot.indicators.atr14 = (
            self._atr.latest(
                market_data
            )
        )

        # -----------------------------------------------------
        # Session VWAP
        # -----------------------------------------------------

        snapshot.indicators.vwap = (
            self._calculate_session_vwap(
                candles
            )
        )

        return snapshot

    # ---------------------------------------------------------
    # Session VWAP
    # ---------------------------------------------------------

    @staticmethod
    def _calculate_session_vwap(candles):

        if not candles:

            return None

        latest_candle = candles[-1]

        latest_date = (
            latest_candle.timestamp.date()
        )

        cumulative_price_volume = 0.0
        cumulative_volume = 0.0

        for candle in candles:

            if candle.timestamp.date() != latest_date:

                continue

            volume = float(
                candle.volume
            )

            if volume <= 0:

                continue

            typical_price = (
                float(candle.high)
                + float(candle.low)
                + float(candle.close)
            ) / 3.0

            cumulative_price_volume += (
                typical_price
                * volume
            )

            cumulative_volume += volume

        if cumulative_volume <= 0:

            return None

        return (
            cumulative_price_volume
            / cumulative_volume
        )
