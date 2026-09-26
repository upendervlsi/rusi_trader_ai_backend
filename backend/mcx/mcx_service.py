"""
============================================================
RUSI Trader AI - MCX Market Service
============================================================

MCX-only market service.

Stages:
    Stage 1:
        MCX contract resolution
        ->
        live market data
        ->
        UI-ready market state

    Stage 1A:
        recent MCX candle data

    Stage 1B:
        real MCX technical indicators

    Stage 1C:
        real MCX intelligence

Execution remains disabled.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.mcx.mcx_instruments import MCX_INSTRUMENTS
from backend.mcx.mcx_market_data import McxMarketData
from backend.mcx.mcx_indicators import McxIndicatorEngine
from backend.mcx.mcx_intelligence import McxIntelligenceEngine
from backend.mcx.mcx_option_selector import McxOptionSelector


def _to_float(value: Any) -> float | None:
    """Safely convert a value to float."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_value(
    data: Any,
    keys: tuple[str, ...],
) -> Any:
    """Recursively search a nested SmartAPI response."""

    if isinstance(data, dict):
        lowered = {
            str(key).lower(): value
            for key, value in data.items()
        }

        for key in keys:
            if key.lower() in lowered:
                return lowered[key.lower()]

        for value in data.values():
            result = _find_value(value, keys)

            if result is not None:
                return result

    elif isinstance(data, list):
        for item in data:
            result = _find_value(item, keys)

            if result is not None:
                return result

    return None


def _extract_ltp(
    ltp_response: Any,
    quote_response: Any,
) -> float | None:
    """Extract LTP from available broker responses."""

    value = _find_value(
        ltp_response,
        ("ltp",),
    )

    if value is None:
        value = _find_value(
            quote_response,
            ("ltp",),
        )

    return _to_float(value)


def _extract_change(
    quote_response: Any,
) -> float | None:
    """Extract percentage change when available."""

    value = _find_value(
        quote_response,
        (
            "percentChange",
            "percent_change",
            "changePercent",
            "change_percentage",
        ),
    )

    return _to_float(value)


def _extract_volume(
    quote_response: Any,
) -> float | None:
    """Extract volume when available."""

    value = _find_value(
        quote_response,
        (
            "volume",
            "tradeVolume",
            "tradedVolume",
            "totalTradedVolume",
        ),
    )

    return _to_float(value)


def _extract_candle_rows(
    candle_response: Any,
) -> list[dict[str, Any]]:
    """
    Extract and normalize SmartAPI OHLCV candle rows.

    Expected broker response:

        {
            "status": true,
            "message": "SUCCESS",
            "errorcode": "",
            "data": [
                [
                    timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume
                ],
                ...
            ]
        }

    Invalid rows are ignored.
    """

    if not isinstance(candle_response, dict):
        return []

    raw_data = candle_response.get("data")

    if not isinstance(raw_data, list):
        return []

    rows: list[dict[str, Any]] = []

    for item in raw_data:
        if not isinstance(item, (list, tuple)):
            continue

        if len(item) < 6:
            continue

        try:
            rows.append(
                {
                    "timestamp": item[0],
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5]),
                }
            )

        except (TypeError, ValueError):
            continue

    return rows


class McxService:
    """
    Top-level isolated MCX service.

    Responsibilities:
        - contract resolution
        - live market data
        - candle retrieval
        - technical indicators
        - MCX intelligence

    Does NOT:
        - submit orders
        - create paper orders
        - modify positions
        - modify NIFTY
        - modify Stock Options
        - modify Midcap
    """

    def __init__(self) -> None:
        self._market_data = McxMarketData()
        self._indicator_engine = McxIndicatorEngine()
        self._intelligence_engine = McxIntelligenceEngine()
        self._option_selector = McxOptionSelector()

    # =========================================================
    # MARKET SNAPSHOT
    # =========================================================

    def get_market(self) -> dict[str, Any]:
        """
        Build the complete MCX market response.

        Technical indicators are calculated independently
        for Crude Oil Mini, Gold Mini and Silver Mini.

        Intelligence is intentionally not executed here.
        The dedicated /api/mcx/intelligence endpoint uses
        get_intelligence().
        """

        instruments: list[dict[str, Any]] = []

        successful = 0
        indicators_ready = 0

        for definition in MCX_INSTRUMENTS:

            try:
                # -------------------------------------------------
                # Live market snapshot
                # -------------------------------------------------

                ltp_response = self._market_data.get_ltp(
                    definition.key
                )

                quote_response = self._market_data.get_quote(
                    definition.key
                )

                ltp = _extract_ltp(
                    ltp_response,
                    quote_response,
                )

                change = _extract_change(
                    quote_response
                )

                volume = _extract_volume(
                    quote_response
                )

                if ltp is not None:
                    successful += 1

                # -------------------------------------------------
                # MCX candle data
                # -------------------------------------------------

                indicator_snapshot = None

                try:
                    candle_rows = self.get_candles(
                        key=definition.key,
                    )

                    indicator_snapshot = (
                        self._indicator_engine.calculate(
                            candle_rows
                        )
                    )

                except Exception:
                    indicator_snapshot = None

                # -------------------------------------------------
                # Indicator values
                # -------------------------------------------------

                if (
                    indicator_snapshot is not None
                    and indicator_snapshot.ready
                ):
                    indicators_ready += 1

                indicator_data = (
                    indicator_snapshot.to_dict()
                    if indicator_snapshot is not None
                    else {}
                )

                ema20 = indicator_data.get("ema20")
                ema50 = indicator_data.get("ema50")
                vwap = indicator_data.get("vwap")
                rsi = indicator_data.get("rsi")
                macd = indicator_data.get("macd")
                macd_signal = indicator_data.get(
                    "macd_signal"
                )
                macd_histogram = indicator_data.get(
                    "macd_histogram"
                )
                atr = indicator_data.get("atr")

                candle_volume = indicator_data.get(
                    "volume"
                )

                volume_average = indicator_data.get(
                    "volume_average"
                )

                volume_expansion = indicator_data.get(
                    "volume_expansion"
                )

                price_momentum = indicator_data.get(
                    "price_momentum"
                )

                display_volume = (
                    volume
                    if volume is not None
                    else candle_volume
                )

                resolved_instrument = self._market_data.instruments[
                    definition.key
                ]

                instruments.append(
                    {
                        "key": definition.key,
                        "name": definition.name,
                        "symbol": definition.symbol,
                        "analysis_symbol": definition.symbol,
                        "emoji": definition.emoji,
                        "exchange": resolved_instrument.exchange,
                        "token": resolved_instrument.token,
                        "resolved_symbol": resolved_instrument.symbol,

                        "ltp": ltp,
                        "change": change,
                        "volume": display_volume,

                        "indicator_status": (
                            "READY"
                            if (
                                indicator_snapshot is not None
                                and indicator_snapshot.ready
                            )
                            else "WAITING"
                        ),

                        "ema20": ema20,
                        "ema50": ema50,

                        "ema": (
                            f"EMA20 {ema20:.2f} | "
                            f"EMA50 {ema50:.2f}"
                            if (
                                isinstance(
                                    ema20,
                                    (int, float),
                                )
                                and isinstance(
                                    ema50,
                                    (int, float),
                                )
                            )
                            else None
                        ),

                        "vwap": vwap,
                        "rsi": rsi,
                        "macd": macd,
                        "macd_signal": macd_signal,
                        "macd_histogram": macd_histogram,
                        "atr": atr,

                        "volume_average": volume_average,
                        "volume_expansion": volume_expansion,
                        "price_momentum": price_momentum,

                        "indicator_candle_count": (
                            indicator_data.get(
                                "candle_count"
                            )
                        ),

                        "trend": None,
                        "momentum": None,
                        "structure": None,

                        "signal": "WAIT",
                        "qualified": 0,
                        "confidence": None,

                        "entry": None,
                        "stop_loss": None,
                        "target": None,
                        "risk_reward": None,

                        "execution_status": "NOT ACTIVE",
                        "pnl": None,
                    }
                )

            except Exception as exc:

                instruments.append(
                    {
                        "key": definition.key,
                        "name": definition.name,
                        "symbol": definition.symbol,
                        "emoji": definition.emoji,
                        "exchange": "MCX",
                        "token": None,
                        "resolved_symbol": None,

                        "ltp": None,
                        "change": None,
                        "volume": None,

                        "indicator_status": "WAITING",

                        "ema20": None,
                        "ema50": None,
                        "ema": None,
                        "vwap": None,
                        "rsi": None,
                        "macd": None,
                        "macd_signal": None,
                        "macd_histogram": None,
                        "atr": None,

                        "volume_average": None,
                        "volume_expansion": None,
                        "price_momentum": None,
                        "indicator_candle_count": None,

                        "trend": None,
                        "momentum": None,
                        "structure": None,

                        "signal": "WAIT",
                        "qualified": 0,
                        "confidence": None,

                        "entry": None,
                        "stop_loss": None,
                        "target": None,
                        "risk_reward": None,

                        "execution_status": "NOT ACTIVE",
                        "pnl": None,

                        "error": str(exc),
                    }
                )

        # =====================================================
        # MARKET DATA STATUS
        # =====================================================

        if successful == len(MCX_INSTRUMENTS):
            data_status = "CONNECTED"

        elif successful > 0:
            data_status = "PARTIAL"

        else:
            data_status = "DISCONNECTED"

        # =====================================================
        # INDICATOR STATUS
        # =====================================================

        if indicators_ready == len(MCX_INSTRUMENTS):
            indicator_status = "READY"

        elif indicators_ready > 0:
            indicator_status = "PARTIAL"

        else:
            indicator_status = "WAITING"

        return {
            "market": "MCX",
            "status": "LIVE",
            "data_status": data_status,
            "last_update": datetime.now().isoformat(),
            "paper_trading": True,

            "runtime": {
                "market_data": (
                    "LIVE"
                    if successful > 0
                    else "WAITING"
                ),

                "candle_builder": (
                    "LIVE"
                    if successful > 0
                    else "WAITING"
                ),

                "indicators": indicator_status,

                "intelligence": "WAITING",
                "decision": "WAITING",
                "risk": "WAITING",
                "execution": "DISABLED",
            },

            "instruments": instruments,
        }

    # =========================================================
    # MCX INTELLIGENCE
    # =========================================================

    def get_intelligence(self) -> dict[str, Any]:
        """
        Build the complete MCX intelligence response.

        Analysis is performed independently for:
            - CRUDEOILM
            - GOLDM
            - SILVERM

        Qualification remains per-instrument.

        This method performs analysis only.

        It does NOT:
            - submit orders
            - create paper orders
            - modify positions
            - modify risk manager state
            - modify NIFTY
            - modify Stock Options
            - modify Midcap
        """

        instruments: list[dict[str, Any]] = []

        successful_market = 0
        indicators_ready = 0
        intelligence_ready = 0

        for definition in MCX_INSTRUMENTS:

            try:
                # -------------------------------------------------
                # Live market data
                # -------------------------------------------------

                ltp_response = self._market_data.get_ltp(
                    definition.key
                )

                quote_response = self._market_data.get_quote(
                    definition.key
                )

                ltp = _extract_ltp(
                    ltp_response,
                    quote_response,
                )

                change = _extract_change(
                    quote_response
                )

                volume = _extract_volume(
                    quote_response
                )

                if ltp is not None:
                    successful_market += 1

                # -------------------------------------------------
                # Candles
                #
                # McxMarketData.get_candles() returns the raw
                # candle list directly, not a SmartAPI envelope.
                # -------------------------------------------------

                candle_data = self._market_data.get_candles(
                    definition.key
                )

                if not isinstance(candle_data, list):
                    raise RuntimeError(
                        "Invalid MCX candle data: "
                        f"expected list, got "
                        f"{type(candle_data).__name__}"
                    )

                candle_rows = []

                for item in candle_data:
                    if not isinstance(item, (list, tuple)):
                        continue

                    if len(item) < 6:
                        continue

                    try:
                        candle_rows.append(
                            {
                                "timestamp": item[0],
                                "open": float(item[1]),
                                "high": float(item[2]),
                                "low": float(item[3]),
                                "close": float(item[4]),
                                "volume": float(item[5]),
                            }
                        )
                    except (TypeError, ValueError):
                        continue

                # -------------------------------------------------
                # Indicators
                # -------------------------------------------------

                indicator_snapshot = (
                    self._indicator_engine.calculate(
                        candle_rows
                    )
                )

                indicator_data = (
                    indicator_snapshot.to_dict()
                )

                if indicator_snapshot.ready:
                    indicators_ready += 1

                # -------------------------------------------------
                # Intelligence
                # -------------------------------------------------

                intelligence = (
                    self._intelligence_engine.analyze(
                        candle_rows,
                        indicator_data,
                    )
                )

                intelligence_ready += 1

                # -------------------------------------------------
                # MCX OPTION SELECTION
                #
                # Intelligence decides the underlying direction
                # and qualification.
                #
                # The isolated MCX selector resolves the actual
                # option contract only after qualification.
                #
                # BUY  -> CE
                # SELL -> PE
                # WAIT / unqualified -> no option
                #
                # No broker order is submitted here.
                # -------------------------------------------------
                option_selection = None

                if (
                    ltp is not None
                    and intelligence.signal in ("BUY", "SELL")
                    and intelligence.qualified == 1
                ):
                    try:
                        option_selection = self._option_selector.select(
                            analysis_symbol=definition.symbol,
                            signal=intelligence.signal,
                            qualified=intelligence.qualified,
                            underlying_price=float(ltp),
                        )
                    except Exception:
                        option_selection = None

                # -------------------------------------------------
                # Indicator values
                # -------------------------------------------------

                ema20 = indicator_data.get("ema20")
                ema50 = indicator_data.get("ema50")

                candle_volume = indicator_data.get(
                    "volume"
                )

                display_volume = (
                    volume
                    if volume is not None
                    else candle_volume
                )

                # -------------------------------------------------
                # Final instrument response
                # -------------------------------------------------

                instruments.append(
                    {
                        # Identity
                        "key": definition.key,
                        "name": definition.name,
                        "symbol": definition.symbol,
                        "emoji": definition.emoji,

                        "exchange": "MCX",

                        "token": (
                            getattr(
                                self._market_data.instruments.get(
                                    definition.key
                                ),
                                "token",
                                None,
                            )
                            if hasattr(
                                self._market_data.instruments,
                                "get",
                            )
                            else None
                        ),

                        "resolved_symbol": (
                            getattr(
                                self._market_data.instruments.get(
                                    definition.key
                                ),
                                "symbol",
                                None,
                            )
                            if hasattr(
                                self._market_data.instruments,
                                "get",
                            )
                            else None
                        ),

                        # Actual MCX option trade information.
                        #
                        # These fields are populated only when the isolated
                        # MCX option selector resolves a real contract.
                        "trade_type": (
                            "OPTION"
                            if option_selection is not None
                            else "PENDING"
                        ),
                        "option_type": (
                            option_selection.option_type
                            if option_selection is not None
                            else None
                        ),
                        "strike": (
                            option_selection.strike
                            if option_selection is not None
                            else None
                        ),
                        "expiry": (
                            option_selection.expiry
                            if option_selection is not None
                            else None
                        ),
                        "trade_symbol": (
                            option_selection.trade_symbol
                            if option_selection is not None
                            else None
                        ),
                        "option_token": (
                            option_selection.token
                            if option_selection is not None
                            else None
                        ),
                        "option_lot_size": (
                            option_selection.lot_size
                            if option_selection is not None
                            else None
                        ),

                        # Live market
                        "ltp": ltp,
                        "change": change,
                        "volume": display_volume,

                        # Indicators
                        "indicator_status": (
                            "READY"
                            if indicator_snapshot.ready
                            else "WAITING"
                        ),

                        "ema20": ema20,
                        "ema50": ema50,

                        "ema": (
                            f"EMA20 {ema20:.2f} | "
                            f"EMA50 {ema50:.2f}"
                            if (
                                isinstance(
                                    ema20,
                                    (int, float),
                                )
                                and isinstance(
                                    ema50,
                                    (int, float),
                                )
                            )
                            else None
                        ),

                        "vwap": indicator_data.get(
                            "vwap"
                        ),
                        "rsi": indicator_data.get(
                            "rsi"
                        ),
                        "macd": indicator_data.get(
                            "macd"
                        ),
                        "macd_signal": indicator_data.get(
                            "macd_signal"
                        ),
                        "macd_histogram": indicator_data.get(
                            "macd_histogram"
                        ),
                        "atr": indicator_data.get(
                            "atr"
                        ),

                        "volume_average": indicator_data.get(
                            "volume_average"
                        ),
                        "volume_expansion": indicator_data.get(
                            "volume_expansion"
                        ),
                        "price_momentum": indicator_data.get(
                            "price_momentum"
                        ),

                        "indicator_candle_count": (
                            indicator_data.get(
                                "candle_count"
                            )
                        ),

                        # Intelligence
                        "signal": intelligence.signal,
                        "qualified": int(
                            intelligence.qualified
                        ),
                        "confidence": intelligence.confidence,

                        "trend": intelligence.trend,
                        "momentum": intelligence.momentum,
                        "structure": intelligence.structure,

                        "breakout": intelligence.breakout,
                        "reversal": intelligence.reversal,
                        "volume_state": intelligence.volume_state,
                        "price_action": intelligence.price_action,

                        "support": intelligence.support,
                        "resistance": intelligence.resistance,

                        "entry": intelligence.entry,
                        "stop_loss": intelligence.stop_loss,
                        "target": intelligence.target,
                        "risk_reward": intelligence.risk_reward,

                        "evidence": intelligence.evidence,
                        "reasons": intelligence.reasons,

                        # Execution remains disabled
                        "execution_status": "NOT ACTIVE",
                        "pnl": None,
                    }
                )

            except Exception as exc:

                instruments.append(
                    {
                        "key": definition.key,
                        "name": definition.name,
                        "symbol": definition.symbol,
                        "emoji": definition.emoji,

                        "exchange": "MCX",
                        "token": None,
                        "resolved_symbol": None,

                        "ltp": None,
                        "change": None,
                        "volume": None,

                        "indicator_status": "WAITING",

                        "ema20": None,
                        "ema50": None,
                        "ema": None,
                        "vwap": None,
                        "rsi": None,
                        "macd": None,
                        "macd_signal": None,
                        "macd_histogram": None,
                        "atr": None,

                        "volume_average": None,
                        "volume_expansion": None,
                        "price_momentum": None,
                        "indicator_candle_count": None,

                        "signal": "WAIT",
                        "qualified": 0,
                        "confidence": None,

                        "trend": None,
                        "momentum": None,
                        "structure": None,

                        "breakout": None,
                        "reversal": None,
                        "volume_state": None,
                        "price_action": None,

                        "support": None,
                        "resistance": None,

                        "entry": None,
                        "stop_loss": None,
                        "target": None,
                        "risk_reward": None,

                        "evidence": [],
                        "reasons": [
                            (
                                "MCX_INTELLIGENCE_ERROR:"
                                f"{type(exc).__name__}:"
                                f"{exc}"
                            )
                        ],

                        "execution_status": "NOT ACTIVE",
                        "pnl": None,

                        "error": str(exc),
                    }
                )

        # =====================================================
        # Runtime status
        # =====================================================

        if successful_market == len(MCX_INSTRUMENTS):
            market_status = "LIVE"
        elif successful_market > 0:
            market_status = "PARTIAL"
        else:
            market_status = "WAITING"

        if indicators_ready == len(MCX_INSTRUMENTS):
            indicator_status = "READY"
        elif indicators_ready > 0:
            indicator_status = "PARTIAL"
        else:
            indicator_status = "WAITING"

        if intelligence_ready == len(MCX_INSTRUMENTS):
            intelligence_status = "READY"
        elif intelligence_ready > 0:
            intelligence_status = "PARTIAL"
        else:
            intelligence_status = "WAITING"

        risk_ready = sum(
            1
            for item in instruments
            if (
                item.get("entry") is not None
                and item.get("stop_loss") is not None
                and item.get("target") is not None
                and item.get("risk_reward") is not None
            )
        )

        if risk_ready == len(MCX_INSTRUMENTS):
            risk_status = "READY"
        elif risk_ready > 0:
            risk_status = "PARTIAL"
        else:
            risk_status = "WAITING"

        return {
            "market": "MCX",
            "status": "LIVE",
            "data_status": (
                "CONNECTED"
                if successful_market == len(MCX_INSTRUMENTS)
                else (
                    "PARTIAL"
                    if successful_market > 0
                    else "DISCONNECTED"
                )
            ),
            "last_update": datetime.now().isoformat(),
            "paper_trading": True,

            "runtime": {
                "market_data": market_status,
                "candle_builder": market_status,
                "indicators": indicator_status,
                "intelligence": intelligence_status,
                "decision": intelligence_status,
                "risk": risk_status,
                "execution": "DISABLED",
            },

            "instruments": instruments,
        }

    # =========================================================
    # CANDLE DATA
    # =========================================================

    def get_candles(
        self,
        key: str,
        interval: str = "FIVE_MINUTE",
        lookback_minutes: int = 300,
    ) -> Any:
        """
        Return recent candle data for one supported MCX
        instrument.

        The public service keeps the interval argument for
        compatibility, but the current McxMarketData layer
        uses its fixed FIVE_MINUTE broker interval internally.

        The raw SmartAPI response is intentionally preserved
        because the public candle API already exposes this
        structure.

        Indicator and intelligence processing extracts the
        response["data"] rows separately.
        """

        return self._market_data.get_candles(
            key=key,
            lookback_minutes=lookback_minutes,
        )
