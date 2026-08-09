"""
============================================================
RUSI Trader AI

Market Data Service

Single service used by the REST API to expose the
authoritative runtime market snapshot.

All market data is read from the runtime snapshot.

Technical indicators are read from:
    snapshot.indicators

Option analytics are read from:
    snapshot.analysis.options
============================================================
"""

from trading.runtime.runtime_manager import RuntimeManager


class MarketDataService:

    def __init__(self):

        self._runtime = RuntimeManager()

    # ---------------------------------------------------------
    # Runtime Snapshot
    # ---------------------------------------------------------

    @property
    def _snapshot(self):

        state = self._runtime.get_state()

        if state.snapshot is None:

            raise RuntimeError(
                "Runtime market snapshot is not available."
            )

        return state.snapshot

    # ---------------------------------------------------------
    # Market
    # ---------------------------------------------------------

    def get_market(self):

        s = self._snapshot

        return {

            "market_status":
                getattr(
                    s,
                    "market_status",
                    "CLOSED",
                ),

            "data_status":
                getattr(
                    s,
                    "data_status",
                    "LIVE",
                ),

            "live_price":
                getattr(
                    s,
                    "live_price",
                    getattr(
                        s.latest_candle,
                        "close",
                        0.0,
                    ),
                ),

            "latest_close":
                getattr(
                    s.latest_candle,
                    "close",
                    0.0,
                ),

            "sma20":
                getattr(
                    s.indicators,
                    "sma20",
                    0.0,
                ),

            "sma50":
                getattr(
                    s.indicators,
                    "sma50",
                    0.0,
                ),

            "ema20":
                getattr(
                    s.indicators,
                    "ema20",
                    0.0,
                ),

            "ema50":
                getattr(
                    s.indicators,
                    "ema50",
                    0.0,
                ),

            "market_structure":
                getattr(
                    s.analysis,
                    "market_structure",
                    "UNKNOWN",
                ),

            "updated_time":
                getattr(
                    s,
                    "updated_time",
                    "",
                ),
        }

    # ---------------------------------------------------------
    # Indicators
    # ---------------------------------------------------------

    def get_indicators(self):

        s = self._snapshot

        indicators = s.indicators

        return {

            "ema20":
                getattr(
                    indicators,
                    "ema20",
                    0.0,
                ),

            "ema50":
                getattr(
                    indicators,
                    "ema50",
                    0.0,
                ),

            "sma20":
                getattr(
                    indicators,
                    "sma20",
                    0.0,
                ),

            "sma50":
                getattr(
                    indicators,
                    "sma50",
                    0.0,
                ),

            "vwap":
                getattr(
                    indicators,
                    "vwap",
                    0.0,
                ),

            "data_status":
                getattr(
                    s,
                    "data_status",
                    "LIVE",
                ),

            "updated_time":
                getattr(
                    s,
                    "updated_time",
                    "",
                ),
        }

    # ---------------------------------------------------------
    # Momentum
    # ---------------------------------------------------------

    def get_momentum(self):

        s = self._snapshot

        indicators = s.indicators

        return {

            "rsi":
                getattr(
                    indicators,
                    "rsi14",
                    0.0,
                ),

            "macd":
                getattr(
                    indicators,
                    "macd",
                    0.0,
                ),

            "adx":
                getattr(
                    indicators,
                    "adx14",
                    0.0,
                ),

            "atr":
                getattr(
                    indicators,
                    "atr14",
                    0.0,
                ),
        }

    # ---------------------------------------------------------
    # Options
    # ---------------------------------------------------------

    def get_options(self):

        s = self._snapshot

        #
        # Authoritative option-analysis container.
        #
        analysis = getattr(
            s,
            "analysis",
            None,
        )

        option_data = getattr(
            analysis,
            "options",
            None,
        ) if analysis is not None else None

        #
        # If the option analyzer has produced an
        # AnalyzerResult, its values are stored in
        # the metadata dictionary.
        #

        metadata = getattr(
            option_data,
            "metadata",
            None,
        )

        if not isinstance(
            metadata,
            dict,
        ):

            metadata = {}

        #
        # Return only values actually published
        # by the runtime.
        #
        # Do NOT use the old backend/services/models
        # MarketSnapshot fields.
        #

        return {

            "pcr":
                self._numeric_value(
                    metadata.get("pcr"),
                ),

            "oi":
                self._numeric_value(
                    metadata.get(
                        "open_interest"
                    ),
                ),

            "change_oi":
                self._numeric_value(
                    metadata.get(
                        "change_oi"
                    ),
                ),

            "iv":
                self._numeric_value(
                    metadata.get(
                        "implied_volatility"
                    ),
                ),

            "max_pain":
                self._numeric_value(
                    metadata.get(
                        "max_pain"
                    ),
                ),
        }

    # ---------------------------------------------------------
    # Numeric Value Helper
    # ---------------------------------------------------------

    @staticmethod
    def _numeric_value(value):

        if value is None:

            return 0.0

        try:

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0
