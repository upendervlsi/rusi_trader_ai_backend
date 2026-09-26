"""
============================================================

RUSI Trader AI

Persistent Market Candle Cache

Purpose:
    Persist one-minute market candles across backend restarts.

The cache protects the trading engine from repeatedly requesting
large historical ranges from the broker API.

============================================================
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


class MarketCandleCache:

    def __init__(
        self,
        symbol: str,
        token: str,
        interval: str = "ONE_MINUTE",
    ):

        safe_symbol = (
            str(symbol)
            .replace("/", "_")
            .replace(" ", "_")
            .replace(":", "_")
        )

        safe_token = str(token)

        filename = (
            f"{safe_symbol}_{safe_token}_{interval}.json"
        )

        self.path = (
            Path("data")
            / "market_cache"
            / filename
        )

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    def load(self):

        try:

            if not self.path.exists():
                return None

            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:

                payload = json.load(file)

            candles = payload.get("candles")

            if not isinstance(candles, list):
                return None

            valid = []

            for candle in candles:

                if (
                    isinstance(candle, list)
                    and len(candle) >= 6
                ):

                    valid.append(candle)

            if not valid:
                return None

            return valid

        except Exception:

            return None

    # ---------------------------------------------------------
    # MERGE
    # ---------------------------------------------------------

    def merge_and_save(self, candles):

        if not candles:
            return False

        try:

            existing = self.load() or []

            merged = {}

            for candle in existing:
                if (
                    isinstance(candle, list)
                    and len(candle) >= 6
                ):
                    merged[str(candle[0])] = candle

            for candle in candles:
                if (
                    isinstance(candle, list)
                    and len(candle) >= 6
                ):
                    merged[str(candle[0])] = candle

            ordered = sorted(
                merged.values(),
                key=lambda candle: str(candle[0]),
            )

            return self.save(ordered)

        except Exception:
            return False

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    def save(self, candles):

        if not candles:
            return False

        try:

            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            payload = {
                "version": 1,
                "interval": "ONE_MINUTE",
                "candle_count": len(candles),
                "candles": candles,
            }

            fd, temp_name = tempfile.mkstemp(
                prefix=".market_cache_",
                suffix=".tmp",
                dir=str(self.path.parent),
            )

            try:

                with os.fdopen(
                    fd,
                    "w",
                    encoding="utf-8",
                ) as file:

                    json.dump(
                        payload,
                        file,
                        separators=(",", ":"),
                    )

                    file.flush()
                    os.fsync(file.fileno())

                os.replace(
                    temp_name,
                    self.path,
                )

            except Exception:

                try:
                    os.unlink(temp_name)
                except OSError:
                    pass

                raise

            return True

        except Exception:

            return False
