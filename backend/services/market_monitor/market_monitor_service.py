"""
RUSI Trader AI

Market Monitor Service

Provides market quotes for the Dashboard.

The Trading Runtime is the single authoritative
source for the latest market state.

Data flow:

    MarketDataEngine
            |
            v
    ExecutionManager
            |
            v
    RuntimeManager
            |
            v
    MarketMonitorService
            |
            v
    Dashboard API
            |
            v
          Flutter
"""

from backend.models.market_quote_model import (
    MarketQuoteModel,
)

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)


class MarketMonitorService:
    """
    Provides market quotes for the dashboard.

    This service does not request market data directly
    from the broker.

    It reads the latest published Trading Runtime state.
    """

    def __init__(self):

        self._facade = TradingEngineFacade()

    # ---------------------------------------------------------
    # Dashboard Quotes
    # ---------------------------------------------------------

    def get_market_quotes(self):

        state = (
            self._facade.get_runtime_state()
        )

        snapshot = state.snapshot

        # -----------------------------------------------------
        # Runtime not ready
        # -----------------------------------------------------

        if snapshot is None:

            return []

        # -----------------------------------------------------
        # Instrument
        # -----------------------------------------------------

        if state.instrument is None:

            return []

        # -----------------------------------------------------
        # Live Price
        #
        # Use the price published by MarketDataEngine.
        #
        # Do NOT use snapshot.latest_candle.close here.
        # That value belongs to the historical analysis
        # pipeline.
        # -----------------------------------------------------

        live_price = getattr(
            state,
            "live_price",
            None,
        )

        # -----------------------------------------------------
        # Fallback
        #
        # If live price is unavailable, use the latest
        # candle close rather than returning an invalid
        # dashboard quote.
        # -----------------------------------------------------

        if live_price is None:

            live_price = (
                snapshot.latest_candle.close
                if snapshot.latest_candle is not None
                else None
            )

        # -----------------------------------------------------
        # Signal
        # -----------------------------------------------------

        signal = None

        if state.recommendation:

            signal = (
                state.recommendation.recommendation
            )

        # -----------------------------------------------------
        # Market Structure
        # -----------------------------------------------------

        market_structure = (
            snapshot.analysis.market_structure
        )

        if (
            market_structure
            and market_structure.bullish_structure
        ):

            trend = "BULLISH"

        elif (
            market_structure
            and market_structure.bearish_structure
        ):

            trend = "BEARISH"

        else:

            trend = "NEUTRAL"

        # -----------------------------------------------------
        # Dashboard Quote
        # -----------------------------------------------------

        quote = MarketQuoteModel(

            symbol=state.instrument.symbol,

            exchange=state.instrument.exchange,

            last_price=live_price,

            signal=signal,

            trend=trend,

            updated_time=state.updated_time,

        )

        return [quote]
