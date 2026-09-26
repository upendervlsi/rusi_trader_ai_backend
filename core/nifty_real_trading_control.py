from __future__ import annotations

import json
import os
from pathlib import Path


class NiftyRealTradingControl:
    """
    Persistent control for NEW NIFTY real-trading entries.

    Safety policy:
        - Missing state file -> DISABLED.
        - Invalid/corrupt state file -> DISABLED.
        - Real trading becomes enabled only after an
          explicit persisted enable.
    """

    DEFAULT_PATH = Path(
        "runs/runtime/NIFTY_FNO_real_trading_control.json"
    )

    VERSION = 1
    MARKET = "NIFTY_FNO"

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path or self.DEFAULT_PATH)

    def _default_payload(self) -> dict:
        return {
            "version": self.VERSION,
            "market": self.MARKET,
            "enabled": False,
        }

    def load(self) -> dict:
        if not self.path.exists():
            return self._default_payload()

        try:
            with self.path.open("r") as fp:
                payload = json.load(fp)
        except (OSError, json.JSONDecodeError):
            return self._default_payload()

        if not isinstance(payload, dict):
            return self._default_payload()

        if int(payload.get("version", 0) or 0) != self.VERSION:
            return self._default_payload()

        if str(payload.get("market") or "") != self.MARKET:
            return self._default_payload()

        enabled = payload.get("enabled")

        if not isinstance(enabled, bool):
            return self._default_payload()

        return {
            "version": self.VERSION,
            "market": self.MARKET,
            "enabled": enabled,
        }

    def is_enabled(self) -> bool:
        return bool(self.load()["enabled"])

    def save(self, enabled: bool) -> bool:
        enabled = bool(enabled)

        payload = {
            "version": self.VERSION,
            "market": self.MARKET,
            "enabled": enabled,
        }

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        with temp_path.open("w") as fp:
            json.dump(
                payload,
                fp,
                indent=2,
                sort_keys=True,
            )
            fp.flush()
            os.fsync(fp.fileno())

        os.replace(
            temp_path,
            self.path,
        )

        return enabled
