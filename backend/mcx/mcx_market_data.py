"""
RUSI Trader AI - MCX Market Data

MCX-only market-data adapter.

Supported instruments:
    CRUDEOILM
    GOLDM
    SILVERM

Architecture:
    SessionManager
        ↓
    SmartConnect
        ↓
    SmartApiClient
        ↓
    AngelDataSource
        ↓
    McxMarketData

Important:
- Uses the existing RUSI broker architecture.
- Does not create a new broker/login implementation.
- Does not modify NIFTY, Stock Options, or Midcap.
- Public get_candles() contract returns only the candle list.
- MCX historical-data pacing/retry is isolated to this adapter.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Any
from zoneinfo import ZoneInfo

from providers.angel.session_manager import SessionManager
from providers.angel.smartapi_client import SmartApiClient
from providers.angel.angel_datasource import AngelDataSource

from backend.mcx.mcx_instruments import (
    MCX_INSTRUMENTS,
    McxInstrumentResolver,
)


class McxMarketData:
    """
    MCX market-data service.

    Resolves the current MCX futures contracts and creates
    an AngelDataSource for each supported instrument.

    Historical-data request pacing and rate-limit recovery are
    intentionally isolated here so existing RUSI market-data
    domains remain unchanged.
    """

    INTERVAL = "FIVE_MINUTE"

    # ---------------------------------------------------------
    # MCX historical-data protection
    # ---------------------------------------------------------
    REQUEST_DELAY_SECONDS = 3.0
    MAX_RATE_LIMIT_RETRIES = 2
    RATE_LIMIT_BACKOFF_SECONDS = (8.0, 15.0)

    _request_lock = Lock()
    _last_historical_request_time: float | None = None

    INDIA_TZ = ZoneInfo("Asia/Kolkata")

    def __init__(self) -> None:
        # ---------------------------------------------------------
        # Existing RUSI broker architecture
        # ---------------------------------------------------------
        self._session = SessionManager()

        # SessionManager owns authentication and returns the
        # process-wide authenticated SmartConnect instance.
        smart_api = self._session.connect()

        # SmartApiClient wraps SmartConnect and owns token
        # recovery/retry behavior.
        self._client = SmartApiClient(
            smart_api,
            self._session,
        )

        # ---------------------------------------------------------
        # MCX instrument resolution
        # ---------------------------------------------------------
        self._resolver = McxInstrumentResolver()

        self._instruments = self._resolver.resolve_all()

        # ---------------------------------------------------------
        # MCX datasource per resolved instrument
        # ---------------------------------------------------------
        self._data_sources: dict[str, AngelDataSource] = {}

        for definition in MCX_INSTRUMENTS:
            instrument = self._instruments[definition.key]

            self._data_sources[definition.key] = AngelDataSource(
                client=self._client,
                instrument=instrument,
            )

    # ============================================================
    # PROPERTIES
    # ============================================================

    @property
    def instruments(self):
        """Return resolved MCX instruments."""
        return self._instruments

    # ============================================================
    # HISTORICAL REQUEST PROTECTION
    # ============================================================

    @classmethod
    def _wait_for_request_slot(cls) -> None:
        """
        Enforce a minimum delay between MCX historical-data requests.

        This limiter is intentionally local to MCX and does not alter
        the shared SmartAPI client or any other RUSI trading domain.
        """

        with cls._request_lock:
            now = time.monotonic()

            if cls._last_historical_request_time is not None:
                elapsed = now - cls._last_historical_request_time
                remaining = cls.REQUEST_DELAY_SECONDS - elapsed

                if remaining > 0:
                    time.sleep(remaining)

            cls._last_historical_request_time = time.monotonic()

    @staticmethod
    def _is_rate_limit_error(exc: Exception) -> bool:
        """
        Detect SmartAPI rate-limit/access-denied responses.

        Detection is intentionally conservative and based only on
        known rate-limit wording observed in the MCX path.
        """

        message = str(exc).lower()

        rate_limit_markers = (
            "access denied because of exceeding access rate",
            "exceeding access rate",
            "rate limit",
            "too many requests",
            "429",
        )

        return any(
            marker in message
            for marker in rate_limit_markers
        )

    def _get_historical_data_safe(
        self,
        datasource: AngelDataSource,
        *,
        from_datetime: datetime,
        to_datetime: datetime,
    ) -> Any:
        """
        Request MCX historical candles with isolated pacing and
        rate-limit recovery.

        Retry policy:
            initial request
            ↓
            8 second backoff
            ↓
            retry
            ↓
            15 second backoff
            ↓
            final retry

        Non-rate-limit errors are raised immediately.
        """

        for attempt in range(
            self.MAX_RATE_LIMIT_RETRIES + 1
        ):
            self._wait_for_request_slot()

            try:
                return datasource.get_historical_data(
                    interval=self.INTERVAL,
                    from_datetime=from_datetime,
                    to_datetime=to_datetime,
                )

            except Exception as exc:
                if not self._is_rate_limit_error(exc):
                    raise

                if attempt >= self.MAX_RATE_LIMIT_RETRIES:
                    raise

                backoff = self.RATE_LIMIT_BACKOFF_SECONDS[attempt]

                print(
                    "MCX HISTORICAL RATE LIMIT: "
                    f"attempt={attempt + 1} "
                    f"backoff={backoff}s"
                )

                time.sleep(backoff)

    # ============================================================
    # CANDLE DATA
    # ============================================================

    def get_candles(
        self,
        key: str,
        lookback_minutes: int = 360,
    ) -> list[list[Any]]:
        """
        Return historical MCX candles.

        Parameters
        ----------
        key:
            MCX instrument key:
                crude
                gold
                silver

        lookback_minutes:
            Historical window. Default is 360 minutes,
            providing enough data for the MCX indicator layer.

        Returns
        -------
        list[list[Any]]
            Raw candle rows from SmartAPI:

            [
                [
                    timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume,
                ],
                ...
            ]

        The SmartAPI response envelope is intentionally removed.

        SmartAPI:
            {
                "status": True,
                "message": "SUCCESS",
                "errorcode": "",
                "data": [...]
            }

        Public contract:
            [...]
        """

        if key not in self._data_sources:
            raise ValueError(
                f"Unsupported MCX instrument key: {key}"
            )

        datasource = self._data_sources[key]

        # ---------------------------------------------------------
        # MCX market time
        #
        # AWS may run in UTC. Use explicit India market time so
        # historical windows are aligned with the MCX session.
        # ---------------------------------------------------------
        to_datetime = datetime.now(
            self.INDIA_TZ
        ).replace(tzinfo=None)

        from_datetime = (
            to_datetime
            - timedelta(minutes=lookback_minutes)
        )

        # ---------------------------------------------------------
        # Protected MCX historical request
        # ---------------------------------------------------------
        response = self._get_historical_data_safe(
            datasource,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
        )

        # ---------------------------------------------------------
        # Validate SmartAPI envelope
        # ---------------------------------------------------------
        if not isinstance(response, dict):
            raise RuntimeError(
                "Invalid SmartAPI historical-data response: "
                f"expected dict, got {type(response).__name__}"
            )

        if not response.get("status"):
            raise RuntimeError(
                "MCX historical-data request failed: "
                f"{response}"
            )

        data = response.get("data")

        if data is None:
            raise RuntimeError(
                "MCX historical-data response contains no data."
            )

        if not isinstance(data, list):
            raise RuntimeError(
                "Invalid MCX candle payload: "
                f"expected list, got {type(data).__name__}"
            )

        # ---------------------------------------------------------
        # Normalize only at the adapter boundary.
        #
        # Do NOT alter candle values here.
        # mcx_indicators.py owns candle normalization.
        # ---------------------------------------------------------
        return data

    # ============================================================
    # LTP
    # ============================================================

    def get_ltp(self, key: str) -> Any:
        """
        Return current LTP for one MCX instrument.
        """

        if key not in self._data_sources:
            raise ValueError(
                f"Unsupported MCX instrument key: {key}"
            )

        return self._data_sources[key].get_ltp()

    # ============================================================
    # OPTION LTP
    # ============================================================

    def get_option_ltp(
        self,
        exchange: str,
        symbol: str,
        token: str,
    ) -> Any:
        """
        Fetch current LTP for a resolved MCX option contract.

        This method is deliberately generic at the contract level.
        It does not select the option and does not make a trading
        decision.

        Parameters
        ----------
        exchange:
            Broker exchange segment, normally MCX.

        symbol:
            Actual option trading symbol returned by McxOptionSelector.

        token:
            Actual option token returned by McxOptionSelector.
        """

        exchange = str(exchange or "").strip().upper()
        symbol = str(symbol or "").strip()
        token = str(token or "").strip()

        if not exchange:
            raise ValueError(
                "Option exchange is required."
            )

        if not symbol:
            raise ValueError(
                "Option trading symbol is required."
            )

        if not token:
            raise ValueError(
                "Option token is required."
            )

        return self._client.get_ltp(
            exchange=exchange,
            trading_symbol=symbol,
            symbol_token=token,
        )

    # ============================================================
    # QUOTE
    # ============================================================

    def get_quote(self, key: str) -> Any:
        """
        Return current quote for one MCX instrument.
        """

        if key not in self._data_sources:
            raise ValueError(
                f"Unsupported MCX instrument key: {key}"
            )

        return self._data_sources[key].get_quote()

    # ============================================================
    # ALL MCX CANDLES
    # ============================================================

    def get_all_candles(
        self,
        lookback_minutes: int = 360,
    ) -> dict[str, list[list[Any]]]:
        """
        Fetch candles for all three supported MCX instruments.

        Each instrument is handled independently.
        A failure in one instrument is not silently converted
        into fake data.
        """

        result: dict[str, list[list[Any]]] = {}

        for definition in MCX_INSTRUMENTS:
            result[definition.key] = self.get_candles(
                definition.key,
                lookback_minutes=lookback_minutes,
            )

        return result
