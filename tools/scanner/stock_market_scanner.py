"""
RUSI Trader AI

Dynamic Stock Market Scanner

Stage 4

Scans the complete stock-options underlying universe.

This component:
    - discovers stock underlyings dynamically
    - resolves NSE equity instruments from the master
    - retrieves historical market data
    - builds normalized candles
    - builds market snapshots
    - retrieves live LTP
    - performs no option selection
    - performs no order execution
    - does not modify the existing NIFTY runtime
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from threading import Lock
import time
from typing import Any

from builders.candle_builder import CandleBuilder
from builders.market_snapshot_builder import MarketSnapshotBuilder
from common.logger import get_logger
from common.stock_options_candle_cache import (
    STOCK_OPTIONS_CACHE_FRESHNESS_MINUTES,
    StockOptionsCandleCache,
)
from core.broker_manager import BrokerManager
from providers.angel.angel_datasource import AngelDataSource
from tools.market_universe.instrument_master_manager import (
    InstrumentMasterManager,
)
from tools.market_universe.instrument_master_parser import (
    InstrumentMasterParser,
)
from tools.market_universe.stock_options_universe import (
    StockOptionsUniverse,
)
from trading.context.trading_context import TradingInstrument


logger = get_logger("RUSI")


class StockMarketScanner:

    """
    Dynamic read-only scanner for all stock-option underlyings.

    The stock universe comes exclusively from the instrument master.

    No stock symbols, contracts, expiries, strikes, lot sizes,
    or option directions are hardcoded here.
    """

    #
    # Broker-safe historical request handling.
    #
    # These values follow the proven Market Pulse broker
    # protection pattern without coupling the two modules.
    #

    HISTORICAL_REQUEST_DELAY_SECONDS = 3.0

    # Stage 11C: bound historical API acquisition per scan.
    # This does NOT reduce the 210-stock universe.
    MAX_HISTORICAL_REQUESTS_PER_SCAN = 20

    # A rate-limit response skips that stock for this cycle.
    MAX_RATE_LIMIT_RETRIES = 0

    RATE_LIMIT_BACKOFF_SECONDS = (
        8.0,
        15.0,
    )

    def __init__(
        self,
        history_days: int,
        interval: str,
        request_delay_seconds: float,
    ):

        if history_days <= 0:
            raise ValueError(
                "history_days must be greater than zero"
            )

        if not interval:
            raise ValueError(
                "interval must not be empty"
            )

        if request_delay_seconds < 0:
            raise ValueError(
                "request_delay_seconds must not be negative"
            )

        self._history_days = history_days
        self._interval = interval
        self._request_delay_seconds = request_delay_seconds

        self._lock = Lock()

        self._broker_manager = BrokerManager()

        self._master_manager = (
            InstrumentMasterManager()
        )

        self._parser = (
            InstrumentMasterParser()
        )

        self._parser.load(
            self._master_manager.load_master()
        )

        self._universe = (
            StockOptionsUniverse(
                self._parser
            )
        )

        self._universe.build()

        self._candle_builder = CandleBuilder()

        self._snapshot_builder = (
            MarketSnapshotBuilder()
        )

        self._cache: dict[
            str,
            dict[str, Any],
        ] = {}

        self._last_scan_time = ""

        self._last_historical_request_time = None

        # Stage 11C: historical API budget for each scan cycle.
        self._historical_requests_this_scan = 0

        # Stage 11D: rotating historical acquisition cursor.
        #
        # The complete stock universe is still scanned every cycle.
        # Only the starting point for historical acquisition rotates,
        # preventing the first 20 stocks from monopolizing the budget.
        self._historical_acquisition_cursor = 0

        self._initialized = False

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    @property
    def universe(self):
        return self._universe

    @property
    def last_scan_time(self) -> str:
        return self._last_scan_time

    def get_cached(self) -> list[dict[str, Any]]:

        return [
            self._cache[symbol]
            for symbol in self._universe.stock_symbols
            if symbol in self._cache
        ]

    def scan(self) -> list[dict[str, Any]]:
        """
        Scan every dynamically discovered stock underlying.

        A failure for one stock does not stop the remaining scan.

        Stage 11D:
            Historical acquisition rotates fairly through the
            complete stock universe across scan cycles.

        The complete universe is still evaluated every cycle.

        Historical broker requests remain protected by the
        Stage 11C per-cycle request budget.
        """

        with self._lock:

            self._ensure_broker()

            # Stage 11C:
            # Reset historical acquisition budget for this cycle.
            self._historical_requests_this_scan = 0

            symbols = list(
                self._universe.stock_symbols
            )

            if not symbols:

                self._last_scan_time = self._now()

                return []

            universe_size = len(symbols)

            # Stage 11D:
            # Start this cycle from the persistent cursor.
            cursor = (
                self._historical_acquisition_cursor
                % universe_size
            )

            ordered_symbols = (
                symbols[cursor:]
                + symbols[:cursor]
            )

            results = []

            scan_time = self._now()

            #
            # Stage 11D:
            #
            # This flag is critical.
            #
            # Once the 20-request budget is reached, we record the
            # cursor exactly once. We do NOT recalculate it for all
            # remaining skipped stocks.
            #
            cursor_advanced = False

            for current_index, symbol in enumerate(
                ordered_symbols
            ):

                result = self._scan_stock(
                    symbol=symbol,
                    scan_time=scan_time,
                )

                results.append(result)

                if result.get("status") == "OK":

                    self._cache[symbol] = result

                #
                # Stage 11D:
                #
                # The moment the historical request budget reaches
                # its maximum, the current stock becomes the last
                # acquisition position for this cycle.
                #
                # The next cycle starts with the following stock.
                #
                if (
                    not cursor_advanced
                    and self._historical_requests_this_scan
                    >= self.MAX_HISTORICAL_REQUESTS_PER_SCAN
                ):

                    self._historical_acquisition_cursor = (
                        cursor
                        + current_index
                        + 1
                    ) % universe_size

                    cursor_advanced = True

                    logger.info(
                        "Stock Options Stage 11D: "
                        "historical acquisition budget exhausted "
                        "(%d requests); "
                        "next cycle cursor=%d/%d.",
                        self.MAX_HISTORICAL_REQUESTS_PER_SCAN,
                        self._historical_acquisition_cursor,
                        universe_size,
                    )

            #
            # If the request budget was not exhausted, the complete
            # universe was traversed without needing rotation.
            #
            if not cursor_advanced:

                self._historical_acquisition_cursor = 0

                logger.info(
                    "Stock Options Stage 11D: "
                    "complete universe traversed without exhausting "
                    "historical acquisition budget; "
                    "cursor reset to 0."
                )

            self._last_scan_time = scan_time

            return results

    # ---------------------------------------------------------
    # Stock scan
    # ---------------------------------------------------------

    def _scan_stock(
        self,
        symbol: str,
        scan_time: str,
    ) -> dict[str, Any]:

        try:

            records = (
                self._parser.get_by_exchange_symbol(
                    "NSE",
                    symbol,
                )
            )

            if not records:

                raise RuntimeError(
                    f"No NSE instrument found for {symbol}"
                )

            selected = self._select_nse_record(
                symbol,
                records,
            )

            instrument = TradingInstrument(
                symbol=symbol,
                exchange="NSE",
                token=str(
                    selected["token"]
                ),
                quantity=1,
                order_type="MARKET",
                product_type="INTRADAY",
            )

            datasource = AngelDataSource(
                client=(
                    self._broker_manager
                    .smartapi_client
                ),
                instrument=instrument,
            )

            cache = StockOptionsCandleCache(
                symbol=symbol,
                token=str(selected["token"]),
                interval=self._interval,
            )

            raw_data = cache.load_if_fresh(
                freshness_minutes=(
                    STOCK_OPTIONS_CACHE_FRESHNESS_MINUTES
                ),
            )

            historical_acquired = False

            if raw_data:

                logger.info(
                    "Stock Options candle cache hit for %s",
                    symbol,
                )

            else:

                logger.info(
                    "Stock Options candle cache miss for %s",
                    symbol,
                )

                # Stage 11C: bound expensive historical API
                # acquisition while preserving the full universe.
                if (
                    self._historical_requests_this_scan
                    >= self.MAX_HISTORICAL_REQUESTS_PER_SCAN
                ):
                    logger.info(
                        "Stock Options: historical acquisition "
                        "budget exhausted (%d requests); "
                        "skipping %s for this cycle.",
                        self.MAX_HISTORICAL_REQUESTS_PER_SCAN,
                        symbol,
                    )

                    return {
                        "symbol": symbol,
                        "exchange": "NSE",
                        "token": str(selected["token"]),
                        "display_symbol": selected.get(
                            "display_symbol", ""
                        ),
                        "status": "SKIPPED",
                        "scan_time": scan_time,
                        "skip_reason": (
                            "historical_acquisition_budget_exhausted"
                        ),
                    }

                end_time = datetime.now(UTC)

                start_time = (
                    end_time
                    - timedelta(
                        days=self._history_days
                    )
                )

                self._historical_requests_this_scan += 1

                response = self._get_historical_data_with_retry(
                    datasource=datasource,
                    start_time=start_time,
                    end_time=end_time,
                    symbol=symbol,
                )

                if response is None:
                    return {
                        "symbol": symbol,
                        "exchange": "NSE",
                        "token": str(selected["token"]),
                        "display_symbol": selected.get(
                            "display_symbol", ""
                        ),
                        "status": "SKIPPED",
                        "scan_time": scan_time,
                        "skip_reason": "historical_rate_limit",
                    }

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

                cache.save(
                    raw_data,
                    history_days=self._history_days,
                )

                historical_acquired = True

            candles = (
                self._candle_builder.build(
                    raw_data
                )
            )

            if not candles:

                raise RuntimeError(
                    "CandleBuilder returned no candles"
                )

            snapshot = (
                self._snapshot_builder.build(
                    candles
                )
            )

            live_response = (
                datasource.get_ltp()
            )

            live_price = (
                self._extract_ltp(
                    live_response
                )
            )

            return {
                "symbol": symbol,
                "exchange": "NSE",
                "token": str(
                    selected["token"]
                ),
                "display_symbol": selected.get(
                    "display_symbol",
                    "",
                ),
                "status": "OK",
                "scan_time": scan_time,
                "live_price": live_price,
                "candle_count": len(candles),
                "candles": candles,
                "snapshot": snapshot,
                "historical_acquired": historical_acquired,
            }

        except Exception as exc:

            logger.exception(
                "Stock Market Scanner failed for %s",
                symbol,
            )

            return {
                "symbol": symbol,
                "exchange": "NSE",
                "status": "ERROR",
                "scan_time": scan_time,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Targeted stock scan
    # ---------------------------------------------------------

    def scan_symbols(
        self,
        symbols: list[str],
    ) -> list[dict[str, Any]]:
        """
        Deep-scan only the requested stock symbols.

        This method is intentionally separate from scan().

        It is used by the Top-N stock movement pipeline after
        lightweight live-quote screening has reduced the complete
        stock universe to a small set of candidates.

        Unlike scan(), this method does NOT use the Stage 11C
        historical acquisition budget or Stage 11D cursor.

        Existing scan() behavior remains unchanged.
        """

        with self._lock:

            self._ensure_broker()

            results: list[dict[str, Any]] = []

            if not symbols:
                return results

            scan_time = self._now()

            for symbol in symbols:

                symbol = str(symbol).upper().strip()

                if not symbol:
                    continue

                try:

                    records = (
                        self._parser.get_by_exchange_symbol(
                            "NSE",
                            symbol,
                        )
                    )

                    if not records:
                        raise RuntimeError(
                            f"No NSE instrument found for {symbol}"
                        )

                    selected = self._select_nse_record(
                        symbol,
                        records,
                    )

                    instrument = TradingInstrument(
                        symbol=symbol,
                        exchange="NSE",
                        token=str(selected["token"]),
                        quantity=1,
                        order_type="MARKET",
                        product_type="INTRADAY",
                    )

                    datasource = AngelDataSource(
                        client=self._broker_manager.smartapi_client,
                        instrument=instrument,
                    )

                    cache = StockOptionsCandleCache(
                        symbol=symbol,
                        token=str(selected["token"]),
                        interval=self._interval,
                    )

                    raw_data = cache.load_if_fresh(
                        freshness_minutes=(
                            STOCK_OPTIONS_CACHE_FRESHNESS_MINUTES
                        ),
                    )

                    historical_acquired = False

                    if raw_data:

                        logger.info(
                            "Stock Options targeted scan: "
                            "candle cache hit for %s",
                            symbol,
                        )

                    else:

                        logger.info(
                            "Stock Options targeted scan: "
                            "candle cache miss for %s",
                            symbol,
                        )

                        end_time = datetime.now(UTC)

                        start_time = (
                            end_time
                            - timedelta(days=self._history_days)
                        )

                        response = (
                            self._get_historical_data_with_retry(
                                datasource=datasource,
                                start_time=start_time,
                                end_time=end_time,
                                symbol=symbol,
                            )
                        )

                        if response is None:

                            results.append(
                                {
                                    "symbol": symbol,
                                    "exchange": "NSE",
                                    "token": str(selected["token"]),
                                    "display_symbol": selected.get(
                                        "display_symbol",
                                        "",
                                    ),
                                    "status": "SKIPPED",
                                    "scan_time": scan_time,
                                    "skip_reason": (
                                        "historical_rate_limit"
                                    ),
                                }
                            )

                            continue

                        raw_data = (
                            response.get("data")
                            if isinstance(response, dict)
                            else None
                        )

                        if not raw_data:
                            raise RuntimeError(
                                "No historical candle data returned"
                            )

                        cache.save(
                            raw_data,
                            history_days=self._history_days,
                        )

                        historical_acquired = True

                    candles = self._candle_builder.build(raw_data)

                    if not candles:
                        raise RuntimeError(
                            "CandleBuilder returned no candles"
                        )

                    snapshot = self._snapshot_builder.build(candles)

                    live_response = datasource.get_ltp()

                    live_price = self._extract_ltp(live_response)

                    results.append(
                        {
                            "symbol": symbol,
                            "exchange": "NSE",
                            "token": str(selected["token"]),
                            "display_symbol": selected.get(
                                "display_symbol",
                                "",
                            ),
                            "status": "OK",
                            "scan_time": scan_time,
                            "live_price": live_price,
                            "candle_count": len(candles),
                            "candles": candles,
                            "snapshot": snapshot,
                            "historical_acquired": historical_acquired,
                        }
                    )

                    logger.info(
                        "Stock Options targeted scan: "
                        "%s completed with %d candles",
                        symbol,
                        len(candles),
                    )

                except Exception as exc:

                    logger.exception(
                        "Stock Options targeted scan "
                        "failed for %s",
                        symbol,
                    )

                    results.append(
                        {
                            "symbol": symbol,
                            "exchange": "NSE",
                            "status": "ERROR",
                            "scan_time": scan_time,
                            "error": str(exc),
                        }
                    )

            return results

    # ---------------------------------------------------------
    # Historical broker request
    # ---------------------------------------------------------

    def _get_historical_data_with_retry(
        self,
        datasource,
        start_time: datetime,
        end_time: datetime,
        symbol: str,
    ):
        """
        Retrieve historical candles with broker-safe pacing
        and rate-limit retry handling.

        Only rate-limit failures are retried.
        Other exceptions propagate immediately.
        """

        total_attempts = (
            1 + self.MAX_RATE_LIMIT_RETRIES
        )

        for attempt in range(
            1,
            total_attempts + 1,
        ):

            self._wait_for_historical_request_slot()

            logger.info(
                "Stock Options: Historical request "
                "%s attempt=%d/%d",
                symbol,
                attempt,
                total_attempts,
            )

            try:

                response = (
                    datasource.get_historical_data(
                        interval=self._interval,
                        from_datetime=start_time,
                        to_datetime=end_time,
                    )
                )

                self._last_historical_request_time = (
                    time.monotonic()
                )

                return response

            except Exception as exc:

                self._last_historical_request_time = (
                    time.monotonic()
                )

                if not self._is_rate_limit_error(
                    exc
                ):
                    raise

                if (
                    attempt
                    > self.MAX_RATE_LIMIT_RETRIES
                ):

                    logger.warning(
                        "Stock Options: Historical "
                        "rate limit for %s; skipping "
                        "this stock for the current cycle.",
                        symbol,
                    )

                    return None

                backoff = (
                    self.RATE_LIMIT_BACKOFF_SECONDS[
                        attempt - 1
                    ]
                )

                logger.warning(
                    "Stock Options: Broker rate limit "
                    "for %s | waiting %.1fs before retry",
                    symbol,
                    backoff,
                )

                time.sleep(backoff)

    def _wait_for_historical_request_slot(self):

        """
        Ensure a minimum delay exists between stock
        historical broker requests.
        """

        if (
            self._last_historical_request_time
            is None
        ):
            return

        elapsed = (
            time.monotonic()
            - self._last_historical_request_time
        )

        remaining = (
            self.HISTORICAL_REQUEST_DELAY_SECONDS
            - elapsed
        )

        if remaining <= 0:
            return

        logger.info(
            "Stock Options: Broker request pacing "
            "wait %.1fs",
            remaining,
        )

        time.sleep(remaining)

    @staticmethod
    def _is_rate_limit_error(
        exc: Exception,
    ) -> bool:
        """
        Detect Angel SmartAPI access-rate failures
        without depending on a specific exception class.
        """

        message = str(exc).lower()

        rate_limit_markers = (
            "exceeding access rate",
            "access rate",
            "rate limit",
            "too many requests",
            "too many request",
            "request limit",
            "throttl",
        )

        return any(
            marker in message
            for marker in rate_limit_markers
        )

    # ---------------------------------------------------------
    # NSE record selection
    # ---------------------------------------------------------

    @staticmethod
    def _select_nse_record(
        symbol: str,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:

        exact = [
            record
            for record in records
            if str(
                record.get(
                    "display_symbol",
                    "",
                )
            ).upper()
            == f"{symbol.upper()}-EQ"
        ]

        if exact:
            return exact[0]

        valid = [
            record
            for record in records
            if record.get("token")
        ]

        if not valid:
            raise RuntimeError(
                f"No valid NSE token found for {symbol}"
            )

        return valid[0]

    # ---------------------------------------------------------
    # Broker
    # ---------------------------------------------------------

    def _ensure_broker(self):

        if self._initialized:
            return

        self._broker_manager.initialize()

        self._initialized = True

    # ---------------------------------------------------------
    # LTP
    # ---------------------------------------------------------

    @staticmethod
    def _extract_ltp(
        response,
    ) -> float | None:

        if not isinstance(response, dict):
            return None

        data = response.get("data")

        if not isinstance(data, dict):
            return None

        value = data.get("ltp")

        if value in (None, ""):
            return None

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    # ---------------------------------------------------------
    # Time
    # ---------------------------------------------------------

    @staticmethod
    def _now() -> str:

        return datetime.now(
            UTC
        ).isoformat()
