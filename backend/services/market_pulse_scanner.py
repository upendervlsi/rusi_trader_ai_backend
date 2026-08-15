"""
============================================================
RUSI Trader AI

Market Pulse Scanner

Purpose
-------
Read-only scanner for the seven dashboard markets.

IMPORTANT
---------
This service:

* DOES NOT place orders.
* DOES NOT select the execution market.
* DOES NOT modify TradingEngineService.
* DOES NOT modify RuntimeManager.
* DOES NOT change option execution.

It only obtains market data and publishes analytical
BUY / SELL / HOLD / WAIT information for the dashboard.

Markets
-------
NIFTY
BANKNIFTY
FINNIFTY
MIDCAP NIFTY
SENSEX
BANKEX
CRUDE OIL

============================================================
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any

from common.logger import get_logger

from core.broker_manager import BrokerManager
from builders.candle_builder import CandleBuilder
from builders.market_snapshot_builder import MarketSnapshotBuilder
from tools.market_universe.instrument_resolver import (
    InstrumentResolver,
)

from trading.context.trading_context import TradingInstrument


logger = get_logger("RUSI")


class MarketPulseScanner:

    """
    Read-only seven-market analytical scanner.

    The scanner deliberately does not use the selected
    execution market.

    Each market is resolved independently.
    """

    MARKETS = (
        {
            "id": "NIFTY_FNO",
            "display_name": "NIFTY",
            "symbol": "NIFTY",
            "analysis_exchange": "NSE",
        },
        {
            "id": "BANKNIFTY_FNO",
            "display_name": "BANKNIFTY",
            "symbol": "BANKNIFTY",
            "analysis_exchange": "NSE",
        },
        {
            "id": "FINNIFTY_FNO",
            "display_name": "FINNIFTY",
            "symbol": "FINNIFTY",
            "analysis_exchange": "NSE",
        },
        {
            "id": "MIDCPNIFTY_FNO",
            "display_name": "MIDCAP NIFTY",
            "symbol": "MIDCPNIFTY",
            "analysis_exchange": "NSE",
        },
        {
            "id": "SENSEX_FNO",
            "display_name": "SENSEX",
            "symbol": "SENSEX",
            "analysis_exchange": "BSE",
        },
        {
            "id": "BANKEX_FNO",
            "display_name": "BANKEX",
            "symbol": "BANKEX",
            "analysis_exchange": "BSE",
        },
        {
            "id": "CRUDEOIL_FNO",
            "display_name": "CRUDE OIL",
            "symbol": "CRUDEOIL",
            "analysis_exchange": "MCX",
        },
    )

    INTERVAL = "ONE_MINUTE"

    HISTORY_DAYS = 30

    def __init__(self):

        self._lock = Lock()

        self._broker_manager = BrokerManager()

        self._resolver = InstrumentResolver()

        self._snapshot_builder = (
            MarketSnapshotBuilder()
        )

        self._candle_builder = CandleBuilder()

        self._cache: dict[str, dict[str, Any]] = {}

        self._last_scan_time = ""

        self._initialized = False

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def scan(self) -> list[dict[str, Any]]:
        """
        Scan all configured dashboard markets.

        Returns one normalized dashboard record per market.
        """

        with self._lock:

            self._ensure_broker()

            results = []

            scan_time = self._now()

            for market in self.MARKETS:

                result = self._scan_market(
                    market,
                    scan_time,
                )

                results.append(result)

                #
                # Preserve last good result when a single
                # market temporarily fails.
                #

                if result["status"] != "ERROR":

                    self._cache[
                        market["id"]
                    ] = result

            self._last_scan_time = scan_time

            return results

    def get_cached(self) -> list[dict[str, Any]]:
        """
        Return the latest successful scanner results.

        No broker call is made.
        """

        results = []

        for market in self.MARKETS:

            market_id = market["id"]

            cached = self._cache.get(
                market_id
            )

            if cached is not None:

                results.append(cached)

            else:

                results.append(
                    self._waiting_result(
                        market
                    )
                )

        return results

    def scan_if_needed(
        self,
        max_age_seconds: int = 30,
    ) -> list[dict[str, Any]]:

        if not self._cache:

            return self.scan()

        if not self._last_scan_time:

            return self.scan()

        try:

            last_scan = datetime.fromisoformat(
                self._last_scan_time
            )

            age = (
                datetime.now(UTC)
                - last_scan
            ).total_seconds()

        except Exception:

            return self.scan()

        if age >= max_age_seconds:

            return self.scan()

        return self.get_cached()

    # ---------------------------------------------------------
    # Broker
    # ---------------------------------------------------------

    def _ensure_broker(self):

        if self._initialized:

            return

        logger.info(
            "Market Pulse Scanner : Initializing broker"
        )

        self._broker_manager.initialize()

        self._initialized = True

        logger.info(
            "Market Pulse Scanner : Broker ready"
        )

    # ---------------------------------------------------------
    # Market Scan
    # ---------------------------------------------------------

    def _scan_market(
        self,
        market: dict[str, str],
        scan_time: str,
    ) -> dict[str, Any]:

        market_id = market["id"]

        try:

            logger.info(
                "Market Pulse : Scanning %s",
                market["display_name"],
            )

            #
            # IMPORTANT:
            #
            # Market Pulse analyzes the underlying market.
            #
            # It does NOT resolve or select an option contract.
            #

            logical_instrument = (
                TradingInstrument(

                    symbol=market["symbol"],

                    exchange=(
                        market["analysis_exchange"]
                    ),

                    token="",

                    quantity=1,

                    order_type="MARKET",

                    product_type="INTRADAY",
                )
            )

            instrument = (
                self._resolver.resolve(
                    logical_instrument
                )
            )

            logger.info(
                "Market Pulse : Resolved %s | %s | %s",
                instrument.symbol,
                instrument.exchange,
                instrument.token,
            )

            #
            # Dedicated datasource.
            #
            # This does not touch the execution manager's
            # selected datasource.
            #

            from providers.angel.angel_datasource import (
                AngelDataSource,
            )

            datasource = AngelDataSource(
                client=self._broker_manager.smartapi_client,
                instrument=instrument,
            )

            end_time = datetime.now(UTC)

            start_time = (
                end_time
                - timedelta(
                    days=self.HISTORY_DAYS
                )
            )

            response = (
                datasource.get_historical_data(
                    exchange=instrument.exchange,
                    token=instrument.token,
                    interval=self.INTERVAL,
                    from_datetime=start_time,
                    to_datetime=end_time,
                )
            )

            raw_data = (
                response.get("data")
                if isinstance(
                    response,
                    dict,
                )
                else None
            )

            if not raw_data:

                raise RuntimeError(
                    "No historical candle data returned"
                )

            #
            # Build the same internal Candle objects
            # used by the existing execution pipeline.
            #

            candles = (
                self._candle_builder.build(
                    raw_data
                )
            )

            if not candles:

                raise RuntimeError(
                    "CandleBuilder returned no candles"
                )

            #
            # Build the existing market snapshot.
            #

            snapshot = (
                self._snapshot_builder.build(
                    candles
                )
            )

            #
            # Live price
            #

            live_response = (
                datasource.get_ltp()
            )

            live_price = (
                self._extract_ltp(
                    live_response
                )
            )

            #
            # Use the existing snapshot values.
            #

            signal = self._extract_signal(
                snapshot
            )

            confidence = self._extract_confidence(
                snapshot
            )

            structure = (
                self._extract_structure(
                    snapshot
                )
            )

            status = (
                "LIVE"
                if live_price is not None
                else "HISTORICAL"
            )

            result = {

                "market": market_id,

                "display_name":
                    market["display_name"],

                "signal":
                    signal,

                "confidence":
                    confidence,

                "status":
                    status,

                "updated_time":
                    scan_time,

                "symbol":
                    instrument.symbol,

                "exchange":
                    instrument.exchange,

                "token":
                    str(instrument.token),

                "live_price":
                    live_price,

                "latest_close":
                    self._latest_close(
                        snapshot
                    ),

                "market_structure":
                    structure,

            }

            logger.info(
                "Market Pulse : %s -> %s %.2f%%",
                market["display_name"],
                signal,
                confidence
                if confidence is not None
                else 0.0,
            )

            return result

        except Exception as exc:

            logger.exception(
                "Market Pulse failed for %s",
                market_id,
            )

            return self._error_result(
                market,
                scan_time,
                str(exc),
            )

    # ---------------------------------------------------------
    # Result Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _waiting_result(
        market: dict[str, str],
    ) -> dict[str, Any]:

        return {

            "market":
                market["id"],

            "display_name":
                market["display_name"],

            "signal":
                "WAIT",

            "confidence":
                None,

            "status":
                "WAITING",

            "updated_time":
                "",

            "symbol":
                market["symbol"],

            "exchange":
                market["analysis_exchange"],

            "token":
                "",

            "live_price":
                None,

            "latest_close":
                None,

            "market_structure":
                "UNKNOWN",
        }

    @staticmethod
    def _error_result(
        market: dict[str, str],
        updated_time: str,
        error: str,
    ) -> dict[str, Any]:

        return {

            "market":
                market["id"],

            "display_name":
                market["display_name"],

            "signal":
                "WAIT",

            "confidence":
                None,

            "status":
                "ERROR",

            "updated_time":
                updated_time,

            "symbol":
                market["symbol"],

            "exchange":
                market["analysis_exchange"],

            "token":
                "",

            "live_price":
                None,

            "latest_close":
                None,

            "market_structure":
                "UNKNOWN",

            "error":
                error,
        }

    # ---------------------------------------------------------
    # Snapshot Extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_signal(
        snapshot,
    ) -> str:

        value = getattr(
            snapshot,
            "recommendation",
            None,
        )

        if value is None:

            return "WAIT"

        value = str(value).upper()

        if value not in {
            "BUY",
            "SELL",
            "HOLD",
            "WAIT",
        }:

            return "WAIT"

        return value

    @staticmethod
    def _extract_confidence(
        snapshot,
    ) -> float | None:

        value = getattr(
            snapshot,
            "confidence",
            None,
        )

        if value is None:

            return None

        try:

            return round(
                float(value),
                2,
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    @staticmethod
    def _extract_structure(
        snapshot,
    ) -> str:

        value = getattr(
            snapshot,
            "market_structure",
            None,
        )

        if value:

            return str(value).upper()

        analysis = getattr(
            snapshot,
            "analysis",
            None,
        )

        value = getattr(
            analysis,
            "market_structure",
            None,
        )

        if value:

            return str(value).upper()

        return "UNKNOWN"

    @staticmethod
    def _latest_close(
        snapshot,
    ) -> float | None:

        value = getattr(
            snapshot,
            "latest_close",
            None,
        )

        if value is not None:

            try:

                return float(value)

            except (
                TypeError,
                ValueError,
            ):

                pass

        candle = getattr(
            snapshot,
            "latest_candle",
            None,
        )

        if candle is not None:

            value = getattr(
                candle,
                "close",
                None,
            )

            if value is not None:

                try:

                    return float(value)

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        return None

    @staticmethod
    def _extract_ltp(
        response,
    ) -> float | None:

        if not isinstance(
            response,
            dict,
        ):

            return None

        data = response.get(
            "data"
        )

        if not isinstance(
            data,
            dict,
        ):

            return None

        value = data.get(
            "ltp"
        )

        try:

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None

    @staticmethod
    def _now() -> str:

        return datetime.now(
            UTC
        ).isoformat()
