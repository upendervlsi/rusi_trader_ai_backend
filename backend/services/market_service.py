"""
RUSI Trader AI

Market Service

Provides market information to Flutter.

The Trading Engine is the authoritative source of
market runtime data.

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
    TradingEngineFacade
            |
            v
    MarketService
            |
            v
    Market API
            |
            v
          Flutter

MarketService does NOT request market data directly
from the broker. It only reads the latest published
Trading Runtime state.
"""

from backend.adapters.trading_engine_facade import (
    TradingEngineFacade,
)

from backend.models.market_model import (
    MarketModel,
)

from backend.services.market_session_service import (
    MarketSessionService,
)


class MarketService:
    """
    Provides the latest market state to the API layer.

    Responsibilities
    ----------------
    - Read TradingRuntimeState
    - Determine exchange/session status
    - Extract live price from runtime
    - Extract historical candle information
    - Build MarketModel

    The service does not call the broker directly.
    """

    def __init__(self):

        self._facade = TradingEngineFacade()

        self._session_service = (
            MarketSessionService()
        )

    # -----------------------------------------------------
    # Market
    # -----------------------------------------------------

    def get_market(self):

        state = (
            self._facade.get_runtime_state()
        )

        snapshot = state.snapshot

        # -------------------------------------------------
        # Determine exchange
        # -------------------------------------------------

        exchange = None

        if state.instrument is not None:

            exchange = (
                state.instrument.exchange
            )

        # -------------------------------------------------
        # Market Session Status
        # -------------------------------------------------

        if exchange:

            market_status = (
                self._session_service.get_market_status(
                    exchange
                )
            )

        else:

            market_status = "CLOSED"

        # -------------------------------------------------
        # Runtime Data Status
        # -------------------------------------------------

        data_status = (
            getattr(
                state,
                "data_status",
                "UNKNOWN",
            )
            or "UNKNOWN"
        )

        # -------------------------------------------------
        # Live Price
        #
        # Runtime is the authoritative source.
        # -------------------------------------------------

        live_price = getattr(
            state,
            "live_price",
            None,
        )

        # -------------------------------------------------
        # Runtime snapshot not ready
        # -------------------------------------------------

        if snapshot is None:

            return MarketModel(

                market_status=market_status,

                data_status=data_status,

                live_price=live_price,

                latest_close=None,

                sma20=None,

                sma50=None,

                ema20=None,

                ema50=None,

                market_structure=None,

                updated_time=state.updated_time,

            )

        # -------------------------------------------------
        # Indicators
        # -------------------------------------------------

        indicators = snapshot.indicators

        # -------------------------------------------------
        # Market Structure
        # -------------------------------------------------

        market_structure_result = (
            snapshot.analysis.market_structure
        )

        if (
            market_structure_result
            and market_structure_result.bullish_structure
        ):

            market_structure = "BULLISH"

        elif (
            market_structure_result
            and market_structure_result.bearish_structure
        ):

            market_structure = "BEARISH"

        else:

            market_structure = "NEUTRAL"

        # -------------------------------------------------
        # Latest Candle
        # -------------------------------------------------

        latest_close = None

        if snapshot.latest_candle is not None:

            latest_close = (
                snapshot.latest_candle.close
            )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return MarketModel(

            market_status=market_status,

            data_status=data_status,

            live_price=live_price,

            latest_close=latest_close,

            sma20=indicators.sma20,

            sma50=indicators.sma50,

            ema20=indicators.ema20,

            ema50=indicators.ema50,

            market_structure=market_structure,

            updated_time=state.updated_time,

        )

    # -----------------------------------------------------
    # Runtime
    # -----------------------------------------------------

    def get_runtime(self):

        return (
            self._facade.get_runtime_state()
        )
