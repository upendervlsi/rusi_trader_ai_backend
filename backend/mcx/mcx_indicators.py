"""
============================================================
RUSI Trader AI
MCX Indicator Engine
============================================================

MCX-only technical indicator calculations.

This module is intentionally isolated from the existing
RUSI indicator/momentum services.

Input:
    MCX 5-minute OHLCV candles

Supported candle formats:
    1. SmartAPI list/tuple:
       [timestamp, open, high, low, close, volume]

    2. Dictionary:
       {
           "open": ...,
           "high": ...,
           "low": ...,
           "close": ...,
           "volume": ...
       }

    3. Candle object:
       .open
       .high
       .low
       .close
       .volume

Output:
    Latest technical indicator snapshot

Indicators:
    EMA20
    EMA50
    VWAP
    RSI14
    MACD(12,26,9)
    ATR14
    Volume average
    Volume expansion
    Price momentum

This module does NOT:
    - generate BUY/SELL signals
    - qualify trades
    - calculate risk
    - execute orders
    - modify RuntimeManager
    - modify existing RUSI markets
============================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


# ============================================================
# Data Model
# ============================================================


@dataclass(frozen=True)
class McxIndicatorSnapshot:
    ema20: float | None = None
    ema50: float | None = None
    vwap: float | None = None
    rsi: float | None = None

    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None

    atr: float | None = None

    volume: float | None = None
    volume_average: float | None = None
    volume_expansion: float | None = None

    price_momentum: float | None = None

    candle_count: int = 0
    ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ============================================================
# Engine
# ============================================================


class McxIndicatorEngine:
    """
    Calculates technical indicators from MCX OHLCV candles.

    Candle input can be:
        - SmartAPI list/tuple candles
        - dictionaries
        - objects exposing open/high/low/close/volume
    """

    EMA_FAST = 20
    EMA_SLOW = 50

    RSI_PERIOD = 14
    ATR_PERIOD = 14

    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    VOLUME_PERIOD = 20
    MOMENTUM_PERIOD = 5

    def calculate(
        self,
        candles: Iterable[Any],
    ) -> McxIndicatorSnapshot:

        rows = [
            self._normalize_candle(candle)
            for candle in candles
        ]

        rows = [
            row
            for row in rows
            if row is not None
        ]

        if not rows:
            return McxIndicatorSnapshot()

        closes = [
            row["close"]
            for row in rows
        ]

        highs = [
            row["high"]
            for row in rows
        ]

        lows = [
            row["low"]
            for row in rows
        ]

        volumes = [
            row["volume"]
            for row in rows
        ]

        candle_count = len(rows)

        ema20_series = self._ema_series(
            closes,
            self.EMA_FAST,
        )

        ema50_series = self._ema_series(
            closes,
            self.EMA_SLOW,
        )

        rsi_series = self._rsi_series(
            closes,
            self.RSI_PERIOD,
        )

        atr_series = self._atr_series(
            highs,
            lows,
            closes,
            self.ATR_PERIOD,
        )

        macd_series = self._macd_series(
            closes,
        )

        vwap = self._vwap(
            highs,
            lows,
            closes,
            volumes,
        )

        volume_average = self._average(
            volumes[-self.VOLUME_PERIOD:],
        )

        current_volume = volumes[-1]

        volume_expansion = None

        if (
            volume_average is not None
            and volume_average > 0
        ):
            volume_expansion = (
                current_volume
                / volume_average
            )

        price_momentum = None

        if candle_count > self.MOMENTUM_PERIOD:

            previous_close = closes[
                -self.MOMENTUM_PERIOD - 1
            ]

            if previous_close != 0:

                price_momentum = (
                    (
                        closes[-1]
                        - previous_close
                    )
                    / previous_close
                ) * 100.0

        ema20 = self._last(
            ema20_series
        )

        ema50 = self._last(
            ema50_series
        )

        rsi = self._last(
            rsi_series
        )

        atr = self._last(
            atr_series
        )

        macd = None
        macd_signal = None
        macd_histogram = None

        if macd_series:

            macd = self._last(
                macd_series["macd"]
            )

            macd_signal = self._last(
                macd_series["signal"]
            )

            macd_histogram = self._last(
                macd_series["histogram"]
            )

        ready = (
            candle_count >= self.EMA_SLOW
            and ema20 is not None
            and ema50 is not None
            and rsi is not None
            and atr is not None
            and macd is not None
            and macd_signal is not None
            and macd_histogram is not None
            and vwap is not None
        )

        return McxIndicatorSnapshot(
            ema20=ema20,
            ema50=ema50,
            vwap=vwap,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            atr=atr,
            volume=current_volume,
            volume_average=volume_average,
            volume_expansion=volume_expansion,
            price_momentum=price_momentum,
            candle_count=candle_count,
            ready=ready,
        )

    # ========================================================
    # Candle Normalization
    # ========================================================

    @staticmethod
    def _normalize_candle(
        candle: Any,
    ) -> dict[str, float] | None:

        try:

            # ------------------------------------------------
            # SmartAPI candle format
            #
            # [
            #     timestamp,
            #     open,
            #     high,
            #     low,
            #     close,
            #     volume
            # ]
            # ------------------------------------------------

            if isinstance(
                candle,
                (list, tuple),
            ):

                if len(candle) < 6:
                    return None

                return {
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                }

            # ------------------------------------------------
            # Dictionary candle format
            # ------------------------------------------------

            if isinstance(
                candle,
                dict,
            ):

                return {
                    "open": float(
                        candle["open"]
                    ),
                    "high": float(
                        candle["high"]
                    ),
                    "low": float(
                        candle["low"]
                    ),
                    "close": float(
                        candle["close"]
                    ),
                    "volume": float(
                        candle["volume"]
                    ),
                }

            # ------------------------------------------------
            # Candle object format
            # ------------------------------------------------

            return {
                "open": float(
                    candle.open
                ),
                "high": float(
                    candle.high
                ),
                "low": float(
                    candle.low
                ),
                "close": float(
                    candle.close
                ),
                "volume": float(
                    candle.volume
                ),
            }

        except (
            KeyError,
            TypeError,
            ValueError,
            AttributeError,
            IndexError,
        ):
            return None

    # ========================================================
    # EMA
    # ========================================================

    @staticmethod
    def _ema_series(
        values: list[float],
        period: int,
    ) -> list[float | None]:

        result: list[float | None] = [
            None
        ] * len(values)

        if len(values) < period:
            return result

        seed = (
            sum(values[:period])
            / period
        )

        result[period - 1] = seed

        multiplier = (
            2.0
            / (period + 1.0)
        )

        previous = seed

        for index in range(
            period,
            len(values),
        ):

            current = (
                (
                    values[index]
                    - previous
                )
                * multiplier
            ) + previous

            result[index] = current

            previous = current

        return result

    # ========================================================
    # RSI
    # ========================================================

    @staticmethod
    def _rsi_series(
        values: list[float],
        period: int,
    ) -> list[float | None]:

        result: list[float | None] = [
            None
        ] * len(values)

        if len(values) <= period:
            return result

        gains = []
        losses = []

        for index in range(
            1,
            len(values),
        ):

            change = (
                values[index]
                - values[index - 1]
            )

            gains.append(
                max(change, 0.0)
            )

            losses.append(
                max(-change, 0.0)
            )

        if len(gains) < period:
            return result

        average_gain = (
            sum(gains[:period])
            / period
        )

        average_loss = (
            sum(losses[:period])
            / period
        )

        result[period] = (
            McxIndicatorEngine._rsi_value(
                average_gain,
                average_loss,
            )
        )

        for index in range(
            period,
            len(gains),
        ):

            average_gain = (
                (
                    average_gain
                    * (period - 1)
                )
                + gains[index]
            ) / period

            average_loss = (
                (
                    average_loss
                    * (period - 1)
                )
                + losses[index]
            ) / period

            result[index + 1] = (
                McxIndicatorEngine._rsi_value(
                    average_gain,
                    average_loss,
                )
            )

        return result

    @staticmethod
    def _rsi_value(
        average_gain: float,
        average_loss: float,
    ) -> float:

        if average_loss == 0:
            if average_gain == 0:
                return 50.0
            return 100.0

        relative_strength = (
            average_gain
            / average_loss
        )

        return (
            100.0
            - (
                100.0
                / (1.0 + relative_strength)
            )
        )

    # ========================================================
    # ATR
    # ========================================================

    @staticmethod
    def _atr_series(
        highs: list[float],
        lows: list[float],
        closes: list[float],
        period: int,
    ) -> list[float | None]:

        result: list[float | None] = [
            None
        ] * len(closes)

        if len(closes) <= period:
            return result

        true_ranges = []

        for index in range(
            len(closes)
        ):

            if index == 0:

                true_range = (
                    highs[index]
                    - lows[index]
                )

            else:

                true_range = max(
                    highs[index]
                    - lows[index],

                    abs(
                        highs[index]
                        - closes[index - 1]
                    ),

                    abs(
                        lows[index]
                        - closes[index - 1]
                    ),
                )

            true_ranges.append(
                true_range
            )

        if len(true_ranges) < period:
            return result

        atr = (
            sum(
                true_ranges[:period]
            )
            / period
        )

        result[period - 1] = atr

        for index in range(
            period,
            len(true_ranges),
        ):

            atr = (
                (
                    atr
                    * (period - 1)
                )
                + true_ranges[index]
            ) / period

            result[index] = atr

        return result

    # ========================================================
    # MACD
    # ========================================================

    def _macd_series(
        self,
        values: list[float],
    ) -> dict[str, list[float | None]]:

        fast = self._ema_series(
            values,
            self.MACD_FAST,
        )

        slow = self._ema_series(
            values,
            self.MACD_SLOW,
        )

        macd: list[float | None] = [
            None
        ] * len(values)

        for index in range(
            len(values)
        ):

            if (
                fast[index] is not None
                and slow[index] is not None
            ):

                macd[index] = (
                    fast[index]
                    - slow[index]
                )

        macd_values = [
            value
            for value in macd
            if value is not None
        ]

        signal_values = self._ema_series(
            macd_values,
            self.MACD_SIGNAL,
        )

        signal: list[float | None] = [
            None
        ] * len(values)

        signal_index = 0

        for index in range(
            len(values)
        ):

            if macd[index] is None:
                continue

            if (
                signal_index
                < len(signal_values)
            ):

                signal[index] = (
                    signal_values[
                        signal_index
                    ]
                )

            signal_index += 1

        histogram: list[float | None] = [
            None
        ] * len(values)

        for index in range(
            len(values)
        ):

            if (
                macd[index] is not None
                and signal[index] is not None
            ):

                histogram[index] = (
                    macd[index]
                    - signal[index]
                )

        return {
            "macd": macd,
            "signal": signal,
            "histogram": histogram,
        }

    # ========================================================
    # VWAP
    # ========================================================

    @staticmethod
    def _vwap(
        highs: list[float],
        lows: list[float],
        closes: list[float],
        volumes: list[float],
    ) -> float | None:

        cumulative_volume = 0.0
        cumulative_value = 0.0

        for high, low, close, volume in zip(
            highs,
            lows,
            closes,
            volumes,
        ):

            if volume < 0:
                continue

            typical_price = (
                high
                + low
                + close
            ) / 3.0

            cumulative_value += (
                typical_price
                * volume
            )

            cumulative_volume += volume

        if cumulative_volume <= 0:
            return None

        return (
            cumulative_value
            / cumulative_volume
        )

    # ========================================================
    # Average
    # ========================================================

    @staticmethod
    def _average(
        values: list[float],
    ) -> float | None:

        if not values:
            return None

        return (
            sum(values)
            / len(values)
        )

    # ========================================================
    # Last Valid Value
    # ========================================================

    @staticmethod
    def _last(
        values: list[float | None],
    ) -> float | None:

        for value in reversed(values):

            if value is not None:
                return value

        return None
