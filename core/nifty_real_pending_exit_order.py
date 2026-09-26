"""
============================================================
NIFTY Real Pending Exit Order
============================================================

Persistent state for an accepted-but-unresolved NIFTY Real
SELL order.

This state is intentionally isolated from:

- Paper Trading
- MIDCAP Real Trading
- MCX Real Trading
- Stock Options Real Trading
- NIFTY Real pending ENTRY orders

A pending exit means the broker has accepted a SELL order but
RUSI has not yet confirmed the final broker-side fill status.

The associated Position must remain OPEN until the broker
confirms the SELL fill.
"""

import json
import os
from pathlib import Path


class NiftyRealPendingExitOrder:

    DEFAULT_PATH = Path(
        "runs/runtime/"
        "NIFTY_FNO_real_pending_exit_order.json"
    )

    def __init__(self, path=None):

        self.path = (
            Path(path)
            if path is not None
            else self.DEFAULT_PATH
        )

    # =========================================================
    # LOAD
    # =========================================================

    def load(self):

        if not self.path.exists():
            return None

        try:

            with self.path.open(
                "r",
                encoding="utf-8",
            ) as fp:

                payload = json.load(fp)

        except Exception:
            return None

        if not isinstance(payload, dict):
            return None

        if payload.get("version") != 1:
            return None

        position_id = str(
            payload.get("position_id") or ""
        ).strip()

        order_id = str(
            payload.get("exit_order_id") or ""
        ).strip()

        symbol = str(
            payload.get("symbol") or ""
        ).strip()

        exchange = str(
            payload.get("exchange") or ""
        ).strip().upper()

        token = str(
            payload.get("token") or ""
        ).strip()

        quantity = payload.get("quantity")

        entry_price = payload.get("entry_price")

        exit_reason = str(
            payload.get("exit_reason") or ""
        ).strip()

        if not position_id:
            return None

        if not order_id:
            return None

        if not symbol:
            return None

        if not symbol.upper().startswith("NIFTY"):
            return None

        if symbol.upper().startswith("MIDCPNIFTY"):
            return None

        if exchange != "NFO":
            return None

        if not token:
            return None

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return None

        if quantity <= 0:
            return None

        try:
            entry_price = float(entry_price)
        except (TypeError, ValueError):
            return None

        if entry_price <= 0:
            return None

        if not exit_reason:
            return None

        return {
            "version": 1,
            "position_id": position_id,
            "exit_order_id": order_id,
            "symbol": symbol,
            "exchange": exchange,
            "token": token,
            "quantity": quantity,
            "entry_price": entry_price,
            "exit_reason": exit_reason,
            "created_at": str(
                payload.get("created_at") or ""
            ),
        }

    # =========================================================
    # SAVE
    # =========================================================

    def save(
        self,
        *,
        position_id: str,
        exit_order_id: str,
        symbol: str,
        exchange: str,
        token: str,
        quantity: int,
        entry_price: float,
        exit_reason: str,
        created_at: str,
    ) -> None:

        position_id = str(position_id or "").strip()
        exit_order_id = str(exit_order_id or "").strip()
        symbol = str(symbol or "").strip()
        exchange = str(exchange or "").strip().upper()
        token = str(token or "").strip()
        exit_reason = str(exit_reason or "").strip()

        if not position_id:
            raise ValueError(
                "NIFTY real pending exit requires position_id"
            )

        if not exit_order_id:
            raise ValueError(
                "NIFTY real pending exit requires exit_order_id"
            )

        if not symbol.upper().startswith("NIFTY"):
            raise ValueError(
                "NIFTY real pending exit requires NIFTY symbol"
            )

        if symbol.upper().startswith("MIDCPNIFTY"):
            raise ValueError(
                "NIFTY real pending exit rejects MIDCPNIFTY"
            )

        if exchange != "NFO":
            raise ValueError(
                "NIFTY real pending exit requires NFO"
            )

        if not token:
            raise ValueError(
                "NIFTY real pending exit requires token"
            )

        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError(
                "NIFTY real pending exit requires positive quantity"
            )

        entry_price = float(entry_price)

        if entry_price <= 0:
            raise ValueError(
                "NIFTY real pending exit requires positive entry price"
            )

        if not exit_reason:
            raise ValueError(
                "NIFTY real pending exit requires exit reason"
            )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "version": 1,
            "position_id": position_id,
            "exit_order_id": exit_order_id,
            "symbol": symbol,
            "exchange": exchange,
            "token": token,
            "quantity": quantity,
            "entry_price": entry_price,
            "exit_reason": exit_reason,
            "created_at": str(created_at or ""),
        }

        temporary_path = Path(
            str(self.path) + ".tmp"
        )

        try:

            with temporary_path.open(
                "w",
                encoding="utf-8",
            ) as fp:

                json.dump(
                    payload,
                    fp,
                    indent=2,
                )

                fp.flush()
                os.fsync(fp.fileno())

            os.replace(
                temporary_path,
                self.path,
            )

        finally:

            if temporary_path.exists():

                try:
                    temporary_path.unlink()

                except OSError:
                    pass

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self):

        try:

            if self.path.exists():
                self.path.unlink()

        except OSError:
            pass
