"""
RUSI Trader AI - MCX Observation Recorder.

Purpose:
    Persist MCX intelligence observations for later analysis.

Design:
    - MCX only.
    - Append-only JSONL storage.
    - Candle-aware duplicate protection.
    - No order execution.
    - No strategy modification.
    - No dependency on NIFTY, Stock Options, or Midcap.
    - Missing values remain None.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OBSERVATION_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "mcx"
    / "intelligence_observations.jsonl"
)


class McxObservationRecorder:
    """
    Append MCX intelligence observations to an isolated JSONL file.
    """

    def __init__(
        self,
        observation_file: Path | str = DEFAULT_OBSERVATION_FILE,
    ) -> None:
        self.observation_file = Path(observation_file)

        self.observation_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def record(
        self,
        *,
        instrument: str,
        market: dict[str, Any] | None = None,
        indicators: dict[str, Any] | None = None,
        intelligence: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Record one MCX intelligence observation.

        Duplicate protection:
            If the same instrument and candle timestamp have
            already been recorded, no new observation is written.

        The method does not calculate or alter any trading decision.
        It only stores the values supplied by the MCX pipeline.

        New OHLC fields:
            open
            high
            low
            close

        These values are supplied by the existing MCX candle
        pipeline and do not create any additional market-data
        request.
        """

        market = market or {}
        indicators = indicators or {}
        intelligence = intelligence or {}

        candle_timestamp = market.get("candle_timestamp")

        if self.has_observation(
            instrument=instrument,
            candle_timestamp=candle_timestamp,
        ):
            return None

        observation = {
            "observation_time": datetime.now(
                timezone.utc
            ).isoformat(),

            "market": {
                "name": "MCX",
                "instrument": instrument,
                "symbol": market.get("symbol"),
                "resolved_symbol": market.get(
                    "resolved_symbol"
                ),
                "exchange": market.get(
                    "exchange",
                    "MCX",
                ),
                "token": market.get("token"),
                "candle_timestamp": candle_timestamp,

                # -------------------------------------------------
                # Candle OHLC
                #
                # These are copied from the existing MCX candle
                # pipeline. They do not trigger another API call.
                # -------------------------------------------------
                "open": market.get("open"),
                "high": market.get("high"),
                "low": market.get("low"),
                "close": market.get("close"),

                # Existing market fields remain unchanged.
                "ltp": market.get("ltp"),
                "change": market.get("change"),
                "volume": market.get("volume"),
            },

            "indicators": {
                "candle_count": indicators.get(
                    "candle_count"
                ),
                "ready": indicators.get("ready"),
                "ema20": indicators.get("ema20"),
                "ema50": indicators.get("ema50"),
                "vwap": indicators.get("vwap"),
                "rsi": indicators.get("rsi"),
                "macd": indicators.get("macd"),
                "macd_signal": indicators.get(
                    "macd_signal"
                ),
                "macd_histogram": indicators.get(
                    "macd_histogram"
                ),
                "atr": indicators.get("atr"),
                "volume": indicators.get("volume"),
                "volume_average": indicators.get(
                    "volume_average"
                ),
                "volume_expansion": indicators.get(
                    "volume_expansion"
                ),
                "price_momentum": indicators.get(
                    "price_momentum"
                ),
            },

            "intelligence": {
                "signal": intelligence.get("signal"),
                "qualified": intelligence.get(
                    "qualified"
                ),
                "confidence": intelligence.get(
                    "confidence"
                ),

                "trend": intelligence.get("trend"),
                "momentum": intelligence.get("momentum"),
                "structure": intelligence.get(
                    "structure"
                ),
                "vwap": intelligence.get("vwap"),
                "ema": intelligence.get("ema"),
                "rsi": intelligence.get("rsi"),
                "macd": intelligence.get("macd"),

                "breakout": intelligence.get(
                    "breakout"
                ),
                "reversal": intelligence.get(
                    "reversal"
                ),
                "volume_state": intelligence.get(
                    "volume_state"
                ),
                "price_action": intelligence.get(
                    "price_action"
                ),

                "support": intelligence.get(
                    "support"
                ),
                "resistance": intelligence.get(
                    "resistance"
                ),

                "entry": intelligence.get("entry"),
                "stop_loss": intelligence.get(
                    "stop_loss"
                ),
                "target": intelligence.get("target"),
                "risk_reward": intelligence.get(
                    "risk_reward"
                ),

                "atr": intelligence.get("atr"),
                "volume_expansion": intelligence.get(
                    "volume_expansion"
                ),
                "price_momentum": intelligence.get(
                    "price_momentum"
                ),

                "evidence": list(
                    intelligence.get("evidence") or []
                ),
                "reasons": list(
                    intelligence.get("reasons") or []
                ),
            },
        }

        with self.observation_file.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                json.dumps(
                    observation,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )

        return observation

    def has_observation(
        self,
        *,
        instrument: str,
        candle_timestamp: Any,
    ) -> bool:
        """
        Check whether an observation for the same
        instrument and candle timestamp already exists.

        If candle_timestamp is unavailable, duplicate protection
        is deliberately disabled for that observation.
        """

        if candle_timestamp is None:
            return False

        if not self.observation_file.exists():
            return False

        candle_timestamp_text = str(
            candle_timestamp
        )

        with self.observation_file.open(
            "r",
            encoding="utf-8",
        ) as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                try:
                    record: dict[str, Any] = json.loads(
                        line
                    )
                except json.JSONDecodeError:
                    continue

                market = record.get("market")

                if not isinstance(market, dict):
                    continue

                if market.get("instrument") != instrument:
                    continue

                if str(
                    market.get("candle_timestamp")
                ) == candle_timestamp_text:
                    return True

        return False

    def count(self) -> int:
        """
        Return the number of stored observations.
        """

        if not self.observation_file.exists():
            return 0

        with self.observation_file.open(
            "r",
            encoding="utf-8",
        ) as handle:
            return sum(
                1
                for line in handle
                if line.strip()
            )
