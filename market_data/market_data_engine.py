"""
============================================================
RUSI Trader AI

Market Data Engine

Central market-data acquisition and normalization layer.

Responsibilities
----------------
* Acquire live LTP data.
* Acquire historical candle data.
* Normalize broker responses.
* Report market-data status.
* Keep broker-specific details below the trading engine.
* Never generate BUY/SELL decisions.
* Never place orders.
* Never modify RuntimeManager directly.

============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


# ============================================================
# Market Data Status
# ============================================================

class MarketDataStatus:
    """
    Standard data-status values used by the application.
    """

    LIVE = "LIVE"

    HISTORICAL = "HISTORICAL"

    STALE = "STALE"

    UNAVAILABLE = "UNAVAILABLE"

    UNKNOWN = "UNKNOWN"


# ============================================================
# Live Market Data
# ============================================================

@dataclass(slots=True)
class LiveMarketData:
    """
    Normalized live market-data object.
    """

    symbol: str = ""

    exchange: str = ""

    token: str = ""

    last_price: float = 0.0

    data_status: str = (
        MarketDataStatus.UNKNOWN
    )

    received_time: str = ""

    source: str = "ANGEL_ONE"

    raw_response: Any = None


# ============================================================
# Market Data Engine
# ============================================================

class MarketDataEngine:
    """
    Central market-data engine.

    Broker communication remains inside the datasource.

    This class only consumes normalized datasource
    functionality and provides a stable interface to the
    trading engine.
    """

    def __init__(self, datasource):

        if datasource is None:

            raise ValueError(
                "MarketDataEngine requires "
                "a datasource."
            )

        self._datasource = datasource

    # ---------------------------------------------------------
    # Instrument
    # ---------------------------------------------------------

    @property
    def instrument(self):

        return self._datasource.instrument

    # ---------------------------------------------------------
    # Live LTP
    # ---------------------------------------------------------

    def get_live_ltp(self) -> LiveMarketData:
        """
        Retrieve and normalize the latest traded price.
        """

        instrument = self.instrument

        try:

            response = (
                self._datasource.get_ltp()
            )

        except Exception as exc:

            return LiveMarketData(

                symbol=instrument.symbol,

                exchange=instrument.exchange,

                token=str(
                    instrument.token
                ),

                last_price=0.0,

                data_status=(
                    MarketDataStatus.UNAVAILABLE
                ),

                received_time=self._now(),

                source="ANGEL_ONE",

                raw_response={
                    "error": str(exc),
                },
            )

        price = self._extract_ltp(
            response
        )

        if price is None:

            return LiveMarketData(

                symbol=instrument.symbol,

                exchange=instrument.exchange,

                token=str(
                    instrument.token
                ),

                last_price=0.0,

                data_status=(
                    MarketDataStatus.UNAVAILABLE
                ),

                received_time=self._now(),

                source="ANGEL_ONE",

                raw_response=response,
            )

        return LiveMarketData(

            symbol=instrument.symbol,

            exchange=instrument.exchange,

            token=str(
                instrument.token
            ),

            last_price=price,

            data_status=(
                MarketDataStatus.LIVE
            ),

            received_time=self._now(),

            source="ANGEL_ONE",

            raw_response=response,
        )

    # ---------------------------------------------------------
    # Quote
    # ---------------------------------------------------------

    def get_quote(self) -> dict[str, Any]:
        """
        Retrieve richer market quote information.
        """

        try:

            response = (
                self._datasource.get_quote()
            )

        except Exception as exc:

            return {

                "status":
                    MarketDataStatus.UNAVAILABLE,

                "received_time":
                    self._now(),

                "error":
                    str(exc),

            }

        return {

            "status":
                MarketDataStatus.LIVE,

            "received_time":
                self._now(),

            "symbol":
                self.instrument.symbol,

            "exchange":
                self.instrument.exchange,

            "token":
                str(self.instrument.token),

            "data":
                response,

        }

    # ---------------------------------------------------------
    # LTP Extraction
    # ---------------------------------------------------------

    @classmethod
    def _extract_ltp(
        cls,
        response: Any,
    ) -> float | None:
        """
        Extract LTP from supported SmartAPI response shapes.
        """

        if not isinstance(
            response,
            dict,
        ):

            return None

        data = response.get(
            "data"
        )

        # -----------------------------------------------------
        # Standard:
        #
        # {
        #     "data": {
        #         "ltp": 7439.0
        #     }
        # }
        # -----------------------------------------------------

        if isinstance(
            data,
            dict,
        ):

            value = data.get(
                "ltp"
            )

            price = cls._to_float(
                value
            )

            if price is not None:

                return price

            # -------------------------------------------------
            # Alternative fetched structure
            # -------------------------------------------------

            fetched = data.get(
                "fetched"
            )

            if isinstance(
                fetched,
                list,
            ):

                for item in fetched:

                    if not isinstance(
                        item,
                        dict,
                    ):

                        continue

                    value = item.get(
                        "ltp"
                    )

                    price = cls._to_float(
                        value
                    )

                    if price is not None:

                        return price

        # -----------------------------------------------------
        # Direct:
        #
        # {
        #     "ltp": 7439.0
        # }
        # -----------------------------------------------------

        value = response.get(
            "ltp"
        )

        return cls._to_float(
            value
        )

    # ---------------------------------------------------------
    # Numeric Conversion
    # ---------------------------------------------------------

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float | None:

        if value is None:

            return None

        try:

            result = float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None

        if result <= 0:

            return None

        return result

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    @staticmethod
    def _now() -> str:

        return datetime.now(
            timezone.utc
        ).isoformat()
