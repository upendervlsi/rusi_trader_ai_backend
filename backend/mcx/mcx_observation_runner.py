"""
RUSI Trader AI - MCX Intelligence Observation Runner.

Purpose:
    Run one isolated real-market MCX intelligence cycle and
    persist the resulting observations.

Supported instruments:
    CRUDEOILM
    GOLDM
    SILVERM

Important:
    - MCX only.
    - Uses existing MCX market-data layer.
    - Uses existing MCX indicator engine.
    - Uses existing MCX Intelligence V2.
    - Uses existing observation recorder.
    - No order execution.
    - No RuntimeManager.
    - No API changes.
    - No modification of NIFTY, Stock Options, or Midcap.
"""

from __future__ import annotations

from typing import Any

from backend.mcx.mcx_instruments import MCX_INSTRUMENTS
from backend.mcx.mcx_market_data import McxMarketData
from backend.mcx.mcx_indicators import McxIndicatorEngine
from backend.mcx.mcx_intelligence import McxIntelligenceEngine
from backend.mcx.mcx_observation import McxObservationRecorder


LOOKBACK_MINUTES = 300
INTERVAL = "FIVE_MINUTE"

INSTRUMENT_KEYS = (
    "crude",
    "gold",
    "silver",
)


def _to_dict(value: Any) -> dict[str, Any]:
    """
    Convert supported RUSI result objects to dictionaries.
    """

    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "to_dict"):
        result = value.to_dict()

        if isinstance(result, dict):
            return result

    if hasattr(value, "__dict__"):
        return dict(vars(value))

    return {}


def _latest_candle_values(
    candles: list[Any],
) -> tuple[
    str | None,
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
]:
    """
    Extract timestamp, OHLC and volume from the
    latest candle.

    SmartAPI candle format:

        [
            timestamp,
            open,
            high,
            low,
            close,
            volume,
        ]

    This function only reads the candle already fetched by the
    existing MCX market-data pipeline. It does not make any
    additional broker request.
    """

    if not candles:
        return (
            None,
            None,
            None,
            None,
            None,
            None,
        )

    candle = candles[-1]

    try:
        if isinstance(candle, (list, tuple)):
            if len(candle) < 6:
                return (
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                )

            return (
                str(candle[0]),
                float(candle[1]),
                float(candle[2]),
                float(candle[3]),
                float(candle[4]),
                float(candle[5]),
            )

        if isinstance(candle, dict):
            timestamp = candle.get(
                "timestamp",
                candle.get("time"),
                candle.get("datetime"),
            )

            return (
                str(timestamp)
                if timestamp is not None
                else None,
                float(candle["open"]),
                float(candle["high"]),
                float(candle["low"]),
                float(candle["close"]),
                float(candle["volume"]),
            )

        timestamp = getattr(
            candle,
            "timestamp",
            getattr(
                candle,
                "time",
                None,
            ),
        )

        return (
            str(timestamp)
            if timestamp is not None
            else None,
            float(candle.open),
            float(candle.high),
            float(candle.low),
            float(candle.close),
            float(candle.volume),
        )

    except (
        TypeError,
        ValueError,
        KeyError,
        AttributeError,
        IndexError,
    ):
        return (
            None,
            None,
            None,
            None,
            None,
            None,
        )


def _get_definition(key: str) -> Any:
    """
    Resolve an MCX instrument definition from the existing
    MCX_INSTRUMENTS collection.

    The existing collection is iterable rather than a dictionary,
    so this runner deliberately adapts to that contract without
    modifying mcx_instruments.py.
    """

    for definition in MCX_INSTRUMENTS:
        if getattr(definition, "key", None) == key:
            return definition

    raise KeyError(
        f"Unknown MCX instrument definition: {key}"
    )


def _build_market_record(
    key: str,
    candles: list[Any],
    market_data: McxMarketData,
) -> dict[str, Any]:
    """
    Build market metadata for the observation recorder.

    Contract metadata is taken from the already-resolved
    TradingInstrument held by McxMarketData.

    Price/volume/timestamp/OHLC are taken from the latest
    five-minute candle.
    """

    definition = _get_definition(key)

    resolved_instrument = market_data.instruments[key]

    (
        candle_timestamp,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
    ) = _latest_candle_values(candles)

    return {
        "symbol": definition.symbol,
        "resolved_symbol": resolved_instrument.symbol,
        "exchange": resolved_instrument.exchange,
        "token": resolved_instrument.token,

        "candle_timestamp": candle_timestamp,

        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,

        # Preserve existing meaning of ltp in the observation
        # pipeline: candle close, not a separate tick request.
        "ltp": close_price,

        "change": None,
        "volume": volume,
    }


def run_observation_cycle() -> list[dict[str, Any]]:
    """
    Run one complete observation cycle for all three
    MCX instruments.
    """

    market_data = McxMarketData()
    indicator_engine = McxIndicatorEngine()
    intelligence_engine = McxIntelligenceEngine()
    recorder = McxObservationRecorder()

    observations: list[dict[str, Any]] = []

    print()
    print("=" * 80)
    print("RUSI MCX INTELLIGENCE OBSERVATION CYCLE")
    print("=" * 80)
    print(f"Interval        : {INTERVAL}")
    print(f"Lookback        : {LOOKBACK_MINUTES} minutes")
    print(
        f"Observation file: "
        f"{recorder.observation_file}"
    )
    print("=" * 80)

    for key in INSTRUMENT_KEYS:
        definition = _get_definition(key)

        print()
        print("-" * 80)
        print(
            f"INSTRUMENT: "
            f"{definition.name} "
            f"({definition.symbol})"
        )
        print("-" * 80)

        try:
            candles = market_data.get_candles(
                key,
                lookback_minutes=LOOKBACK_MINUTES,
            )

            if not isinstance(candles, list):
                raise TypeError(
                    "Expected candle list, "
                    f"got {type(candles).__name__}"
                )

            print(
                f"Candles         : {len(candles)}"
            )

            indicators_result = (
                indicator_engine.calculate(
                    candles
                )
            )

            indicators = _to_dict(
                indicators_result
            )

            print(
                f"Indicators ready: "
                f"{indicators.get('ready')}"
            )

            intelligence_result = (
                intelligence_engine.analyze(
                    candles,
                    indicators_result,
                )
            )

            intelligence = _to_dict(
                intelligence_result
            )

            print(
                f"Signal          : "
                f"{intelligence.get('signal')}"
            )

            print(
                f"Qualified       : "
                f"{intelligence.get('qualified')}"
            )

            print(
                f"Confidence      : "
                f"{intelligence.get('confidence')}"
            )

            print(
                f"Trend           : "
                f"{intelligence.get('trend')}"
            )

            print(
                f"Momentum        : "
                f"{intelligence.get('momentum')}"
            )

            print(
                f"Structure       : "
                f"{intelligence.get('structure')}"
            )

            print(
                f"Volume          : "
                f"{intelligence.get('volume_state')}"
            )

            print(
                f"Risk/Reward     : "
                f"{intelligence.get('risk_reward')}"
            )

            market = _build_market_record(
                key,
                candles,
                market_data,
            )

            print(
                f"Resolved Symbol : "
                f"{market.get('resolved_symbol')}"
            )

            print(
                f"Token           : "
                f"{market.get('token')}"
            )

            print(
                f"Candle          : "
                f"{market.get('candle_timestamp')}"
            )

            print(
                f"OHLC            : "
                f"{market.get('open')} / "
                f"{market.get('high')} / "
                f"{market.get('low')} / "
                f"{market.get('close')}"
            )

            observation = recorder.record(
                instrument=definition.symbol,
                market=market,
                indicators=indicators,
                intelligence=intelligence,
            )

            if observation is None:
                print(
                    "Observation     : "
                    "SKIPPED (DUPLICATE CANDLE)"
                )
                continue

            observations.append(observation)

            print(
                "Observation     : RECORDED"
            )

        except Exception as exc:
            print(
                f"Observation     : ERROR - {exc}"
            )

    return observations


if __name__ == "__main__":
    run_observation_cycle()
