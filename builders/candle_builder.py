"""
============================================================

RUSI Trader AI

Candle Builder

Converts broker candle responses into internal Candle
objects and optionally applies the latest live LTP to
the current one-minute candle.

============================================================
"""

from __future__ import annotations

from datetime import datetime, UTC

from common.candle import Candle


class CandleBuilder:

    @staticmethod
    def build(
        raw_candles,
        live_price: float | None = None,
    ):

        candles = []

        if raw_candles is None:
            return candles

        #
        # -----------------------------------------------------
        # Build historical candles
        # -----------------------------------------------------
        #

        for row in raw_candles:

            if not row or len(row) < 6:
                continue

            candles.append(

                Candle(

                    timestamp=(
                        datetime.fromisoformat(
                            row[0]
                        )
                        .astimezone(UTC)
                        .replace(
                            second=0,
                            microsecond=0,
                        )
                    ),

                    open=float(row[1]),

                    high=float(row[2]),

                    low=float(row[3]),

                    close=float(row[4]),

                    volume=int(row[5]),
                )
            )

        #
        # -----------------------------------------------------
        # Apply live LTP
        # -----------------------------------------------------
        #
        # Historical candle data and live LTP are separate
        # broker data paths.
        #
        # The feature engine must see the current market price.
        #
        # We therefore update the current one-minute candle
        # when live_price is available.
        #
        # IMPORTANT:
        # We do NOT create a fake historical candle when there
        # are no historical candles.
        #

        if (
            live_price is not None
            and candles
        ):

            try:

                live_price = float(
                    live_price
                )

                if live_price > 0.0:

                    latest = candles[-1]

                    #
                    # Current UTC minute.
                    #
                    current_minute = (
                        datetime.now(UTC)
                        .replace(
                            second=0,
                            microsecond=0,
                        )
                    )

                    latest_minute = (
                        latest.timestamp
                        .astimezone(UTC)
                        .replace(
                            second=0,
                            microsecond=0,
                        )
                    )

                    #
                    # -------------------------------------------------
                    # Case 1:
                    # Historical API already returned the current
                    # one-minute candle.
                    #
                    # Update its high/low/close.
                    # -------------------------------------------------
                    #

                    if latest_minute == current_minute:

                        latest.high = max(
                            float(latest.high),
                            live_price,
                        )

                        latest.low = min(
                            float(latest.low),
                            live_price,
                        )

                        latest.close = (
                            live_price
                        )

                    #
                    # -------------------------------------------------
                    # Case 2:
                    # Historical API is one or more minutes behind.
                    #
                    # Create a current working candle from the
                    # latest known close and current LTP.
                    #
                    # This candle is used only for the current
                    # intelligence calculation.
                    # -------------------------------------------------
                    #

                    elif latest_minute < current_minute:

                        candles.append(

                            Candle(

                                timestamp=current_minute,

                                open=float(
                                    latest.close
                                ),

                                high=max(
                                    float(
                                        latest.close
                                    ),
                                    live_price,
                                ),

                                low=min(
                                    float(
                                        latest.close
                                    ),
                                    live_price,
                                ),

                                close=live_price,

                                volume=0,
                            )
                        )

                    #
                    # If historical data somehow contains a
                    # future timestamp, do not modify it.
                    #

                    else:

                        pass

            except (
                TypeError,
                ValueError,
                OverflowError,
            ):

                #
                # Never allow live-price enrichment to break
                # the complete trading pipeline.
                #
                pass

        return candles
