"""
============================================================
RUSI Trader AI

Market Pulse Analyzer

Analysis-only engine for the Dashboard Market Pulse.

IMPORTANT
---------
This component is deliberately separated from
ExecutionManager.

It DOES:
    * resolve analysis instruments
    * download market candles
    * build MarketSnapshot
    * run existing intelligence analysis
    * publish signal/confidence to MarketPulseRuntime

It DOES NOT:
    * place orders
    * select option contracts
    * execute futures
    * modify portfolio
    * modify RuntimeManager
    * change the selected execution market

For index markets, analysis uses the NSE/BSE index itself.

CRITICAL
--------
Angel One instrument master contains multiple records for
some indices.

Example:

    NIFTY
        standard index token : 26000
        AMXIDX token         : 99926000

Testing proved that:

    NSE / 26000
        SUCCESS + empty candle data

    NSE / 99926000
        SUCCESS + real candle data

Therefore Market Pulse explicitly prefers the verified
AMXIDX index token for historical analysis.

CRUDE OIL is intentionally not analyzed here until the
real MCX option-chain path is available. No futures fallback
is used.

Broker request protection:
    * requests are paced
    * rate-limit responses are retried
    * one market failure does not stop the remaining markets
============================================================
"""

from __future__ import annotations

import time

from datetime import (
    datetime,
    UTC,
    timedelta,
)

from common.logger import get_logger

from builders.candle_builder import (
    CandleBuilder,
)

from builders.market_snapshot_builder import (
    MarketSnapshotBuilder,
)

from intelligence.intelligence_manager import (
    IntelligenceManager,
)

from providers.angel.session_manager import (
    SessionManager,
)

from providers.angel.smartapi_client import (
    SmartApiClient,
)

from trading.context.trading_context import (
    TradingInstrument,
)

from tools.market_universe.instrument_master_manager import (
    InstrumentMasterManager,
)

from tools.market_universe.instrument_master_parser import (
    InstrumentMasterParser,
)

from backend.services.market_pulse_runtime import (
    MarketPulseRuntime,
)


logger = get_logger("RUSI")


class MarketPulseAnalyzer:

    """
    Analysis-only multi-market analyzer.

    One broker session is reused for all markets in a scan.

    The analyzer is intentionally independent from the
    execution pipeline.
    """

    # ========================================================
    # MARKET UNIVERSE
    # ========================================================

    MARKETS = (
        {
            "market": "NIFTY_FNO",
            "display_name": "NIFTY",
            "symbol": "NIFTY",
            "exchange": "NSE",
        },
        {
            "market": "BANKNIFTY_FNO",
            "display_name": "BANKNIFTY",
            "symbol": "BANKNIFTY",
            "exchange": "NSE",
        },
        {
            "market": "FINNIFTY_FNO",
            "display_name": "FINNIFTY",
            "symbol": "FINNIFTY",
            "exchange": "NSE",
        },
        {
            "market": "MIDCPNIFTY_FNO",
            "display_name": "MIDCAP NIFTY",
            "symbol": "MIDCPNIFTY",
            "exchange": "NSE",
        },
        {
            "market": "SENSEX_FNO",
            "display_name": "SENSEX",
            "symbol": "SENSEX",
            "exchange": "BSE",
        },
        {
            "market": "BANKEX_FNO",
            "display_name": "BANKEX",
            "symbol": "BANKEX",
            "exchange": "BSE",
        },
        {
            "market": "CRUDEOIL_FNO",
            "display_name": "CRUDE OIL",
            "symbol": "CRUDEOIL",
            "exchange": "MCX",
        },
    )

    # ========================================================
    # INDEX EXCHANGES
    # ========================================================

    INDEX_EXCHANGES = {
        "NSE",
        "BSE",
    }

    # ========================================================
    # HISTORICAL DATA
    # ========================================================

    INTERVAL = "ONE_MINUTE"

    #
    # Keep the existing design intent of using enough history
    # for the intelligence engine.
    #
    HISTORY_DAYS = 30

    # ========================================================
    # VERIFIED HISTORICAL INDEX TOKENS
    # ========================================================

    #
    # IMPORTANT:
    #
    # These are NOT execution tokens.
    #
    # They are specifically the index instruments verified
    # against Angel SmartAPI historical candle API.
    #
    # Testing on 2026-08-14 proved:
    #
    # NIFTY 26000     -> empty candles
    # NIFTY 99926000  -> real candles
    #
    # The same AMXIDX convention exists in the instrument
    # master for the other supported indices.
    #

    HISTORICAL_INDEX_TOKENS = {
        (
            "NSE",
            "NIFTY",
        ): "99926000",

        (
            "NSE",
            "BANKNIFTY",
        ): "99926009",

        (
            "NSE",
            "FINNIFTY",
        ): "99926037",

        (
            "NSE",
            "MIDCPNIFTY",
        ): "99926074",

        (
            "BSE",
            "SENSEX",
        ): "99919000",

        (
            "BSE",
            "BANKEX",
        ): "99919012",
    }

    # ========================================================
    # BROKER REQUEST PROTECTION
    # ========================================================

    #
    # Minimum gap between historical requests.
    #
    # Six index markets therefore do not hit SmartAPI as a
    # burst.
    #

    REQUEST_DELAY_SECONDS = 3.0

    #
    # Additional attempts after a rate-limit response.
    #
    # Total attempts:
    #
    #   1 initial
    #   + 2 retries
    #   = 3
    #

    MAX_RATE_LIMIT_RETRIES = 2

    #
    # Retry backoff.
    #

    RATE_LIMIT_BACKOFF_SECONDS = (
        8.0,
        15.0,
    )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        self._runtime = (
            MarketPulseRuntime()
        )

        self._snapshot_builder = (
            MarketSnapshotBuilder()
        )

        self._intelligence = (
            IntelligenceManager()
        )

        self._smart_connect = None

        self._client = None

        self._parser = None

        self._initialized = False

        #
        # Monotonic timestamp of the previous historical
        # request.
        #

        self._last_request_time = None

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def _initialize(self):

        if self._initialized:

            return

        logger.info(
            "Market Pulse : Initializing broker session"
        )

        session_manager = (
            SessionManager()
        )

        self._smart_connect = (
            session_manager.connect()
        )

        self._client = SmartApiClient(
            self._smart_connect
        )

        #
        # Load instrument master once.
        #

        manager = (
            InstrumentMasterManager()
        )

        parser = (
            InstrumentMasterParser()
        )

        parser.load(
            manager.load_master()
        )

        self._parser = parser

        self._initialized = True

        logger.info(
            "Market Pulse : Broker and instrument master ready"
        )

    # ========================================================
    # PUBLIC SCAN
    # ========================================================

    def scan(self):

        """
        Analyze all supported markets.

        A failure in one market must not stop the remaining
        markets.
        """

        self._initialize()

        logger.info(
            "=============================================="
        )

        logger.info(
            "MARKET PULSE SCAN STARTED"
        )

        logger.info(
            "=============================================="
        )

        for market in self.MARKETS:

            market_id = market["market"]

            #
            # CRUDE OIL
            #
            # Do not fall back to futures.
            #

            if market["exchange"] == "MCX":

                self._publish_waiting(
                    market,
                    "OPTION_ANALYSIS_NOT_AVAILABLE",
                )

                continue

            try:

                self._scan_market(
                    market
                )

            except Exception as exc:

                logger.exception(
                    "Market Pulse failed : %s",
                    market_id,
                )

                self._publish_error(
                    market,
                    str(exc),
                )

        logger.info(
            "=============================================="
        )

        logger.info(
            "MARKET PULSE SCAN COMPLETED"
        )

        logger.info(
            "=============================================="
        )

    # ========================================================
    # SINGLE MARKET
    # ========================================================

    def _scan_market(
        self,
        market: dict,
    ):

        market_id = market["market"]

        symbol = market["symbol"]

        exchange = market["exchange"]

        logger.info(
            "Market Pulse : Analyzing %s",
            market_id,
        )

        #
        # Resolve the verified historical index instrument.
        #

        instrument = (
            self._resolve_index(
                symbol=symbol,
                exchange=exchange,
            )
        )

        logger.info(
            "Market Pulse : Resolved %s | %s | %s",
            symbol,
            exchange,
            instrument.token,
        )

        #
        # SmartAPI expects the historical date range in
        # market/local time.
        #
        # Use IST instead of sending UTC timestamps.
        #

        end_time = self._market_now()

        start_time = (
            end_time
            - timedelta(
                days=self.HISTORY_DAYS
            )
        )

        #
        # Protected historical-data request.
        #

        response = (
            self._get_historical_candles_safe(
                market_id=market_id,
                exchange=instrument.exchange,
                symbol_token=instrument.token,
                interval=self.INTERVAL,
                from_datetime=start_time,
                to_datetime=end_time,
            )
        )

        if not response:

            raise RuntimeError(
                "Empty historical response"
            )

        #
        # Broker response must explicitly report success.
        #

        if response.get("status") is False:

            message = response.get(
                "message",
                "Unknown SmartAPI error",
            )

            errorcode = response.get(
                "errorcode",
                "",
            )

            raise RuntimeError(
                "SmartAPI historical request failed: "
                f"{message}"
                + (
                    f" [{errorcode}]"
                    if errorcode
                    else ""
                )
            )

        raw_data = response.get(
            "data"
        )

        if not raw_data:

            raise RuntimeError(
                "No historical candle data"
            )

        logger.info(
            "Market Pulse : %s raw candles=%d",
            market_id,
            len(raw_data),
        )

        #
        # Normalize broker candles.
        #

        candles = (
            CandleBuilder.build(
                raw_data
            )
        )

        if not candles:

            raise RuntimeError(
                "CandleBuilder returned no candles"
            )

        logger.info(
            "Market Pulse : %s candles=%d",
            market_id,
            len(candles),
        )

        #
        # Build market snapshot.
        #

        snapshot = (
            self._snapshot_builder.build(
                candles
            )
        )

        if snapshot is None:

            raise RuntimeError(
                "MarketSnapshotBuilder returned no snapshot"
            )

        #
        # Existing RUSI intelligence engine.
        #
        # Analysis only.
        #

        intelligence = (
            self._intelligence.analyze(
                snapshot
            )
        )

        #
        # Extract intelligence result.
        #

        signal = (
            self._extract_signal(
                intelligence
            )
        )

        confidence = (
            self._extract_confidence(
                intelligence
            )
        )

        trend = (
            self._extract_trend(
                snapshot
            )
        )

        score = (
            self._extract_score(
                intelligence
            )
        )

        reason = (
            self._extract_reason(
                intelligence
            )
        )

        #
        # Latest market price.
        #

        latest_candle = getattr(
            snapshot,
            "latest_candle",
            None,
        )

        if latest_candle is None:

            raise RuntimeError(
                "Snapshot contains no latest candle"
            )

        try:

            last_price = float(
                latest_candle.close
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise RuntimeError(
                "Invalid latest candle close"
            ) from exc

        #
        # Publish to independent Market Pulse runtime.
        #

        self._runtime.publish(

            market_id,

            signal=signal,

            confidence=confidence,

            status="LIVE",

            symbol=symbol,

            exchange=exchange,

            last_price=last_price,

            trend=trend,

            score=score,

            reason=reason,
        )

        logger.info(
            "Market Pulse Result : "
            "%s | %s | confidence=%s | "
            "score=%s | price=%.2f",
            market_id,
            signal,
            self._format_number(
                confidence
            ),
            self._format_number(
                score
            ),
            last_price,
        )

        return {
            "market": market_id,
            "symbol": symbol,
            "exchange": exchange,
            "token": instrument.token,
            "signal": signal,
            "confidence": confidence,
            "score": score,
            "trend": trend,
            "reason": reason,
            "last_price": last_price,
            "candle_count": len(candles),
            "successful_engines": getattr(
                intelligence,
                "successful_engines",
                0,
            ),
            "failed_engines": getattr(
                intelligence,
                "failed_engines",
                0,
            ),
        }

    # ========================================================
    # MARKET TIME
    # ========================================================

    @staticmethod
    def _market_now() -> datetime:

        """
        Return current Indian market time.

        SmartAPI historical requests are sent in the local
        Indian market time rather than UTC.
        """

        from zoneinfo import ZoneInfo

        return datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).replace(
            tzinfo=None
        )

    # ========================================================
    # PROTECTED HISTORICAL REQUEST
    # ========================================================

    def _get_historical_candles_safe(
        self,
        market_id: str,
        exchange: str,
        symbol_token: str,
        interval: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ):

        """
        Get historical candles while protecting SmartAPI
        from rapid repeated requests.

        Only rate-limit failures are retried.

        Other broker/API failures are propagated immediately.
        """

        if self._client is None:

            raise RuntimeError(
                "SmartApiClient is not initialized"
            )

        self._wait_for_request_slot()

        attempt = 0

        while True:

            attempt += 1

            logger.info(
                "Market Pulse : Historical request "
                "%s attempt=%d/%d",
                market_id,
                attempt,
                1 + self.MAX_RATE_LIMIT_RETRIES,
            )

            try:

                response = (
                    self._client.get_historical_candles(

                        exchange=exchange,

                        symbol_token=symbol_token,

                        interval=interval,

                        from_datetime=from_datetime,

                        to_datetime=to_datetime,
                    )
                )

                self._last_request_time = (
                    time.monotonic()
                )

                return response

            except Exception as exc:

                self._last_request_time = (
                    time.monotonic()
                )

                if not self._is_rate_limit_error(
                    exc
                ):

                    raise

                #
                # Rate-limit error.
                #

                if (
                    attempt
                    > self.MAX_RATE_LIMIT_RETRIES
                ):

                    logger.error(
                        "Market Pulse : Rate limit "
                        "retry limit reached for %s",
                        market_id,
                    )

                    raise

                backoff = (
                    self.RATE_LIMIT_BACKOFF_SECONDS[
                        attempt - 1
                    ]
                )

                logger.warning(
                    "Market Pulse : Broker rate limit "
                    "for %s | waiting %.1fs before retry",
                    market_id,
                    backoff,
                )

                time.sleep(
                    backoff
                )

                #
                # Enforce normal request spacing again.
                #

                self._wait_for_request_slot()

    # ========================================================
    # BROKER REQUEST PACING
    # ========================================================

    def _wait_for_request_slot(self):

        """
        Ensure a minimum delay exists between historical
        broker requests.
        """

        if self._last_request_time is None:

            return

        elapsed = (
            time.monotonic()
            - self._last_request_time
        )

        remaining = (
            self.REQUEST_DELAY_SECONDS
            - elapsed
        )

        if remaining <= 0:

            return

        logger.info(
            "Market Pulse : Broker request pacing "
            "wait %.1fs",
            remaining,
        )

        time.sleep(
            remaining
        )

    # ========================================================
    # RATE-LIMIT DETECTION
    # ========================================================

    @staticmethod
    def _is_rate_limit_error(
        exc: Exception,
    ) -> bool:

        """
        Detect Angel SmartAPI access-rate failures without
        depending on a specific SmartAPI exception class.
        """

        message = str(
            exc
        ).lower()

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

    # ========================================================
    # INDEX RESOLVER
    # ========================================================

    def _resolve_index(
        self,
        symbol: str,
        exchange: str,
    ) -> TradingInstrument:

        exchange = str(
            exchange
        ).upper()

        symbol = str(
            symbol
        ).upper()

        if exchange not in self.INDEX_EXCHANGES:

            raise RuntimeError(
                "Market Pulse index resolver "
                "does not support exchange "
                f"{exchange}"
            )

        if self._parser is None:

            raise RuntimeError(
                "Instrument master not initialized"
            )

        #
        # ----------------------------------------------------
        # FIRST:
        # Use explicitly verified historical index token.
        # ----------------------------------------------------
        #

        verified_token = (
            self.HISTORICAL_INDEX_TOKENS.get(
                (
                    exchange,
                    symbol,
                )
            )
        )

        if verified_token:

            matches = (
                self._parser
                .get_by_exchange_symbol(
                    exchange,
                    symbol,
                )
            )

            selected = None

            #
            # Confirm the token exists in the current
            # instrument master.
            #

            for record in matches:

                if str(
                    record.get(
                        "token",
                        "",
                    )
                ) == verified_token:

                    selected = record

                    break

            if selected is None:

                raise RuntimeError(
                    "Verified historical token "
                    f"{verified_token} for "
                    f"{exchange}:{symbol} was not "
                    "found in instrument master"
                )

            logger.info(
                "Market Pulse : Selected index "
                "instrument %s | %s | token=%s | "
                "segment=%s",
                symbol,
                exchange,
                verified_token,
                selected.get(
                    "segment",
                    "",
                ),
            )

            return TradingInstrument(

                symbol=symbol,

                exchange=exchange,

                token=verified_token,

                quantity=1,

                order_type="MARKET",

                product_type="INTRADAY",
            )

        #
        # ----------------------------------------------------
        # FALLBACK:
        # Generic instrument-master lookup.
        #
        # This should only be reached for a newly added
        # index that has not yet received a verified
        # historical token mapping.
        # ----------------------------------------------------
        #

        matches = (
            self._parser
            .get_by_exchange_symbol(
                exchange,
                symbol,
            )
        )

        if not matches:

            raise RuntimeError(
                f"No {exchange} instrument found "
                f"for {symbol}"
            )

        selected = None

        #
        # Prefer AMXIDX records if available.
        #

        for record in matches:

            segment = str(
                record.get(
                    "segment",
                    "",
                )
            ).upper()

            if segment == "AMXIDX":

                selected = record

                break

        #
        # Otherwise prefer exact display-symbol match.
        #

        if selected is None:

            for record in matches:

                display_symbol = str(
                    record.get(
                        "display_symbol",
                        "",
                    )
                ).upper()

                if (
                    display_symbol
                    == symbol
                ):

                    selected = record

                    break

        #
        # Final fallback.
        #

        if selected is None:

            selected = matches[0]

        token = selected.get(
            "token"
        )

        if not token:

            raise RuntimeError(
                "Instrument token missing for "
                f"{exchange}:{symbol}"
            )

        logger.warning(
            "Market Pulse : Using fallback "
            "index instrument %s | %s | token=%s | "
            "segment=%s",
            symbol,
            exchange,
            token,
            selected.get(
                "segment",
                "",
            ),
        )

        return TradingInstrument(

            symbol=symbol,

            exchange=exchange,

            token=str(token),

            quantity=1,

            order_type="MARKET",

            product_type="INTRADAY",
        )

    # ========================================================
    # INTELLIGENCE RESULT HELPERS
    # ========================================================

    @staticmethod
    def _engine_results(
        result,
    ) -> list:

        """
        Extract EngineResult objects from IntelligenceResult.

        IntelligenceManager returns:

            IntelligenceResult
                results[]
                    EngineResult

        This helper intentionally validates the extracted
        collection instead of relying only on attribute
        presence.
        """

        if result is None:

            return []

        #
        # Primary path:
        # IntelligenceResult.results
        #

        results = getattr(
            result,
            "results",
            None,
        )

        if results is not None:

            try:

                extracted = list(
                    results
                )

            except TypeError:

                extracted = []

            if extracted:

                return extracted

        #
        # Backward compatibility:
        # direct EngineResult-like object.
        #

        if any(
            hasattr(
                result,
                attribute,
            )
            for attribute in (
                "signal",
                "recommendation",
                "score",
                "confidence",
            )
        ):

            return [
                result
            ]

        return []

    # ========================================================
    # SIGNAL EXTRACTION
    # ========================================================

    @classmethod
    def _extract_signal(
        cls,
        result,
    ) -> str:

        engines = cls._engine_results(
            result
        )

        if not engines:

            return "WAIT"

        signals = []

        for engine_result in engines:

            value = getattr(
                engine_result,
                "recommendation",
                None,
            )

            if value is None:

                value = getattr(
                    engine_result,
                    "signal",
                    None,
                )

            if value is None:

                continue

            signal = str(
                value
            ).strip().upper()

            if signal:

                signals.append(
                    signal
                )

        if not signals:

            return "WAIT"

        #
        # Normalize common directional values.
        #

        bullish = sum(
            1
            for signal in signals
            if signal in (
                "BUY",
                "BULLISH",
                "LONG",
            )
        )

        bearish = sum(
            1
            for signal in signals
            if signal in (
                "SELL",
                "BEARISH",
                "SHORT",
            )
        )

        sideways = sum(
            1
            for signal in signals
            if signal in (
                "SIDEWAYS",
                "NEUTRAL",
            )
        )

        #
        # Agreement has priority.
        #

        if bullish > bearish and bullish >= sideways:

            return "BULLISH"

        if bearish > bullish and bearish >= sideways:

            return "BEARISH"

        if sideways > bullish and sideways > bearish:

            return "SIDEWAYS"

        #
        # Conflicting intelligence remains WAIT.
        # This is safer than inventing direction.
        #

        return "WAIT"

    # ========================================================
    # CONFIDENCE EXTRACTION
    # ========================================================

    @classmethod
    def _extract_confidence(
        cls,
        result,
    ) -> float | None:

        engines = cls._engine_results(
            result
        )

        if not engines:

            return None

        values = []

        for engine_result in engines:

            value = getattr(
                engine_result,
                "confidence",
                None,
            )

            if value is None:

                continue

            try:

                value = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            #
            # Keep confidence inside the
            # application's 0-100 convention.
            #

            value = max(
                0.0,
                min(
                    value,
                    100.0,
                ),
            )

            values.append(
                value
            )

        if not values:

            return None

        #
        # Aggregate the participating intelligence engines.
        #

        return (
            sum(values)
            / len(values)
        )

    # ========================================================
    # TREND EXTRACTION
    # ========================================================

    @classmethod
    def _extract_trend(
        cls,
        snapshot,
    ) -> str:

        if snapshot is None:

            return "UNKNOWN"

        #
        # Try direct snapshot trend first.
        #

        value = getattr(
            snapshot,
            "trend",
            None,
        )

        if value is not None:

            return str(
                value
            ).upper()

        #
        # Then try snapshot analysis.
        #

        analysis = getattr(
            snapshot,
            "analysis",
            None,
        )

        if analysis is not None:

            value = getattr(
                analysis,
                "trend",
                None,
            )

            if value is not None:

                return str(
                    value
                ).upper()

            value = getattr(
                analysis,
                "market_structure",
                None,
            )

            if value is not None:

                return str(
                    value
                ).upper()

        return "UNKNOWN"

    # ========================================================
    # SCORE EXTRACTION
    # ========================================================

    @classmethod
    def _extract_score(
        cls,
        result,
    ) -> float | None:

        engines = cls._engine_results(
            result
        )

        if not engines:

            return None

        values = []

        for engine_result in engines:

            value = getattr(
                engine_result,
                "score",
                None,
            )

            if value is None:

                continue

            try:

                values.append(
                    float(value)
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

        if not values:

            return None

        #
        # Aggregate the scores from the engines
        # that actually supplied a numeric score.
        #

        return (
            sum(values)
            / len(values)
        )

    # ========================================================
    # REASON EXTRACTION
    # ========================================================

    @classmethod
    def _extract_reason(
        cls,
        result,
    ) -> str:

        engines = cls._engine_results(
            result
        )

        if not engines:

            return ""

        collected = []

        for engine_result in engines:

            value = getattr(
                engine_result,
                "reason",
                None,
            )

            if value:

                collected.append(
                    str(value).strip()
                )

                continue

            reasons = getattr(
                engine_result,
                "reasons",
                None,
            )

            if isinstance(
                reasons,
                (list, tuple),
            ):

                for item in reasons:

                    item = str(
                        item
                    ).strip()

                    if item:

                        collected.append(
                            item
                        )

            elif reasons:

                collected.append(
                    str(
                        reasons
                    ).strip()
                )

        #
        # Remove duplicate reasons while preserving
        # engine/result order.
        #

        unique = []

        seen = set()

        for reason in collected:

            if not reason:

                continue

            if reason in seen:

                continue

            seen.add(
                reason
            )

            unique.append(
                reason
            )

        return " | ".join(
            unique
        )

    # ========================================================

    # ========================================================
    # WAITING STATE
    # ========================================================

    def _publish_waiting(
        self,
        market: dict,
        reason: str,
    ):

        market_id = market[
            "market"
        ]

        symbol = market.get(
            "symbol",
            "",
        )

        exchange = market.get(
            "exchange",
            "",
        )

        self._runtime.publish(

            market_id,

            signal="WAIT",

            confidence=None,

            status="WAITING",

            symbol=symbol,

            exchange=exchange,

            last_price=None,

            trend="",

            score=None,

            reason=reason,
        )

        logger.info(
            "Market Pulse : %s waiting | %s",
            market_id,
            reason,
        )

    # ========================================================
    # ERROR STATE
    # ========================================================

    def _publish_error(
        self,
        market: dict,
        reason: str,
    ):

        market_id = market[
            "market"
        ]

        symbol = market.get(
            "symbol",
            "",
        )

        exchange = market.get(
            "exchange",
            "",
        )

        self._runtime.publish(

            market_id,

            signal="WAIT",

            confidence=None,

            status="ERROR",

            symbol=symbol,

            exchange=exchange,

            last_price=None,

            trend="",

            score=None,

            reason=str(
                reason
            ),
        )

        logger.error(
            "Market Pulse : %s ERROR | %s",
            market_id,
            reason,
        )

    # ========================================================
    # NUMBER FORMATTER
    # ========================================================

    @staticmethod
    def _format_number(
        value,
    ) -> str:

        if value is None:

            return "None"

        try:

            return f"{float(value):.2f}"

        except (
            TypeError,
            ValueError,
        ):

            return str(
                value
            )
