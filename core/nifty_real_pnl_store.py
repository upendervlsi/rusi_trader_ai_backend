from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


class NiftyRealPnlStore:
    """
    Persistent NIFTY Real Trading P&L ledger.

    IMPORTANT:
    - NIFTY Real Trading only.
    - Completely independent from Paper Trading.
    - Does not modify trade_journal.csv.
    - Realized P&L is recorded only after a confirmed broker exit fill.
    - Broker exit Order ID provides idempotency so the same trade
      cannot be counted twice.
    """

    DEFAULT_PATH = Path(
        "runs/runtime/NIFTY_FNO_real_pnl.json"
    )

    VERSION = 1
    TIMEZONE = ZoneInfo("Asia/Kolkata")

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path or self.DEFAULT_PATH)

    def _empty_payload(self) -> dict:
        return {
            "version": self.VERSION,
            "market": "NIFTY_FNO",
            "currency": "INR",
            "cumulative_realized_pnl": 0.0,
            "trades": [],
        }

    def load(self) -> dict:
        if not self.path.exists():
            return self._empty_payload()

        try:
            with self.path.open("r") as fp:
                payload = json.load(fp)
        except (OSError, json.JSONDecodeError):
            return self._empty_payload()

        if not isinstance(payload, dict):
            return self._empty_payload()

        if int(payload.get("version", 0) or 0) != self.VERSION:
            return self._empty_payload()

        if str(payload.get("market") or "") != "NIFTY_FNO":
            return self._empty_payload()

        trades = payload.get("trades")
        if not isinstance(trades, list):
            trades = []

        try:
            cumulative = float(
                payload.get("cumulative_realized_pnl", 0.0) or 0.0
            )
        except (TypeError, ValueError):
            cumulative = 0.0

        return {
            "version": self.VERSION,
            "market": "NIFTY_FNO",
            "currency": "INR",
            "cumulative_realized_pnl": cumulative,
            "trades": trades,
        }

    def _save(self, payload: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

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

        os.replace(temp_path, self.path)

    def record_closed_trade(
        self,
        *,
        position_id: str,
        exit_order_id: str,
        symbol: str,
        quantity: int,
        realized_pnl: float,
        exit_reason: str,
        exit_time: str | None = None,
    ) -> bool:
        """
        Record one confirmed NIFTY Real closed trade.

        Returns:
            True  -> newly recorded
            False -> already recorded / invalid request
        """

        position_id = str(position_id or "").strip()
        exit_order_id = str(exit_order_id or "").strip()
        symbol = str(symbol or "").strip()

        if not position_id:
            raise ValueError(
                "NIFTY Real P&L requires position_id"
            )

        if not exit_order_id:
            raise ValueError(
                "NIFTY Real P&L requires broker exit_order_id"
            )

        if not symbol.startswith("NIFTY"):
            raise ValueError(
                "NIFTY Real P&L accepts only NIFTY symbols"
            )

        if symbol.startswith("MIDCPNIFTY"):
            raise ValueError(
                "NIFTY Real P&L rejects MIDCPNIFTY symbols"
            )

        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError(
                "NIFTY Real P&L quantity must be positive"
            )

        realized_pnl = float(realized_pnl)

        if exit_time:
            timestamp = str(exit_time)
        else:
            timestamp = datetime.now(
                self.TIMEZONE
            ).isoformat()

        try:
            trade_date = datetime.fromisoformat(
                timestamp
            ).astimezone(self.TIMEZONE).date().isoformat()
        except ValueError:
            timestamp = datetime.now(
                self.TIMEZONE
            ).isoformat()
            trade_date = datetime.now(
                self.TIMEZONE
            ).date().isoformat()

        payload = self.load()

        #
        # Idempotency:
        # the same broker exit Order ID must never contribute
        # to P&L more than once.
        #
        for trade in payload["trades"]:
            if str(
                trade.get("exit_order_id") or ""
            ).strip() == exit_order_id:
                return False

        record = {
            "position_id": position_id,
            "exit_order_id": exit_order_id,
            "symbol": symbol,
            "quantity": quantity,
            "realized_pnl": realized_pnl,
            "exit_reason": str(
                exit_reason or "REAL_EXIT"
            ),
            "exit_time": timestamp,
            "trade_date": trade_date,
        }

        payload["trades"].append(record)

        payload["cumulative_realized_pnl"] = float(
            payload["cumulative_realized_pnl"]
        ) + realized_pnl

        self._save(payload)

        return True

    def get_daily_realized_pnl(
        self,
        trade_date: str | None = None,
    ) -> float:
        """
        Return NIFTY Real realized P&L for one IST date.

        Defaults to today in Asia/Kolkata.
        """

        if trade_date is None:
            trade_date = datetime.now(
                self.TIMEZONE
            ).date().isoformat()

        total = 0.0

        for trade in self.load()["trades"]:
            if str(
                trade.get("trade_date") or ""
            ) != str(trade_date):
                continue

            try:
                total += float(
                    trade.get("realized_pnl") or 0.0
                )
            except (TypeError, ValueError):
                continue

        return total

    def get_cumulative_realized_pnl(self) -> float:
        return float(
            self.load()["cumulative_realized_pnl"]
        )

    def get_status(self) -> dict:
        today = datetime.now(
            self.TIMEZONE
        ).date().isoformat()

        payload = self.load()

        return {
            "market": "NIFTY_FNO",
            "currency": "INR",
            "today": today,
            "daily_realized_pnl": self.get_daily_realized_pnl(
                today
            ),
            "cumulative_realized_pnl": float(
                payload["cumulative_realized_pnl"]
            ),
            "closed_trade_count": len(
                payload["trades"]
            ),
        }
