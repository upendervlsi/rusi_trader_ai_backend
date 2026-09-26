"""
Persistent candle cache for the Stock Options observation pipeline.

This cache is intentionally isolated from MarketCandleCache so that
Stock Options changes cannot alter the existing NIFTY V1 path.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, UTC, timedelta
from pathlib import Path


STOCK_OPTIONS_CACHE_FRESHNESS_MINUTES = 15


class StockOptionsCandleCache:

    def __init__(
        self,
        symbol: str,
        token: str,
        interval: str,
        cache_dir: Path | str = Path("data") / "stock_options_market_cache",
    ):
        self.symbol = str(symbol)
        self.token = str(token)
        self.interval = str(interval)

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_symbol = "".join(
            char if char.isalnum() or char in ("_", "-") else "_"
            for char in self.symbol
        )

        safe_token = "".join(
            char if char.isalnum() or char in ("_", "-") else "_"
            for char in self.token
        )

        safe_interval = "".join(
            char if char.isalnum() or char in ("_", "-") else "_"
            for char in self.interval
        )

        self.path = (
            self.cache_dir
            / f"{safe_symbol}_{safe_token}_{safe_interval}.json"
        )

    def load(self) -> list:
        if not self.path.exists():
            return []

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as handle:
                payload = json.load(handle)

            if not isinstance(payload, dict):
                return []

            if payload.get("symbol") != self.symbol:
                return []

            if payload.get("token") != self.token:
                return []

            if payload.get("interval") != self.interval:
                return []

            candles = payload.get("candles")

            if not isinstance(candles, list):
                return []

            valid = []

            for candle in candles:
                if isinstance(candle, list) and len(candle) >= 6:
                    valid.append(candle)

            return valid

        except (
            OSError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ):
            return []

    def load_if_fresh(
        self,
        freshness_minutes: int,
    ) -> list:

        if freshness_minutes <= 0:
            return []

        candles = self.load()

        if not candles:
            return []

        try:
            latest_timestamp = datetime.fromisoformat(
                str(candles[-1][0])
            )

            if latest_timestamp.tzinfo is None:
                latest_timestamp = latest_timestamp.replace(
                    tzinfo=UTC
                )

            latest_timestamp = latest_timestamp.astimezone(UTC)

            age = (
                datetime.now(UTC)
                - latest_timestamp
            )

            if age < timedelta(
                minutes=freshness_minutes
            ):
                return candles

        except (
            TypeError,
            ValueError,
            IndexError,
            OverflowError,
        ):
            pass

        return []

    def save(
        self,
        candles: list,
        history_days: int | None = None,
    ) -> bool:

        valid = [
            candle
            for candle in candles
            if isinstance(candle, list)
            and len(candle) >= 6
        ]

        if not valid:
            return False

        payload = {
            "version": 1,
            "symbol": self.symbol,
            "token": self.token,
            "interval": self.interval,
            "history_days": history_days,
            "captured_at": datetime.now(UTC).isoformat(),
            "candles": valid,
        }

        temp_path = None

        try:
            fd, temp_name = tempfile.mkstemp(
                dir=self.cache_dir,
                prefix=".stock_options_candle_cache_",
                suffix=".tmp",
            )

            temp_path = Path(temp_name)

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    payload,
                    handle,
                    separators=(",", ":"),
                )

            os.replace(
                temp_path,
                self.path,
            )

            return True

        except OSError:

            if temp_path is not None:
                try:
                    temp_path.unlink(
                        missing_ok=True,
                    )
                except OSError:
                    pass

            return False

    def merge_and_save(
        self,
        candles: list,
        history_days: int | None = None,
    ) -> list:

        existing = self.load()

        merged = {}

        for candle in existing + list(candles or []):

            if not isinstance(candle, list):
                continue

            if len(candle) < 6:
                continue

            timestamp = str(candle[0])

            merged[timestamp] = candle

        result = [
            merged[key]
            for key in sorted(merged)
        ]

        self.save(
            result,
            history_days=history_days,
        )

        return result
