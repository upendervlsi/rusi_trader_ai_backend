"""
============================================================
NIFTY Real Trading - Pending Order State
============================================================

Purpose
-------
Persist one unresolved NIFTY Real broker entry order so that
ExecutionManager can reconcile it after a bounded broker
poll or after a service restart.

This module is intentionally isolated from:
    - Paper Trading
    - MIDCAP
    - MCX
    - Stock Options
    - PositionMonitor
    - BrokerManager

It stores broker order identity, requested order details,
the original risk parameters, and the original decision
metadata required to reconstruct the local position after
a confirmed broker fill.

It never invents or persists a broker fill.
============================================================
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class NiftyRealPendingOrder:
    """
    Persistent state for one NIFTY Real pending entry order.

    Only one pending NIFTY Real entry is allowed at a time.
    """

    DEFAULT_PATH = Path(
        "runs/runtime/NIFTY_FNO_real_pending_order.json"
    )

    def __init__(
        self,
        path: str | Path | None = None,
    ):
        self._path = Path(
            path
            if path is not None
            else self.DEFAULT_PATH
        )

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists()

    def load(self) -> dict[str, Any] | None:
        """
        Load the persisted pending order.

        Returns None when no pending order exists or when the
        persisted content is invalid or lacks the original
        decision metadata required for safe recovery.
        """

        if not self._path.exists():
            return None

        try:
            with self._path.open(
                "r",
                encoding="utf-8",
            ) as fp:
                data = json.load(fp)
        except (
            OSError,
            json.JSONDecodeError,
        ):
            return None

        if not isinstance(data, dict):
            return None

        pending_order = data.get("pending_order")

        if not isinstance(
            pending_order,
            dict,
        ):
            return None

        order_id = str(
            pending_order.get(
                "order_id",
                "",
            )
        ).strip()

        symbol = str(
            pending_order.get(
                "symbol",
                "",
            )
        ).strip()

        exchange = str(
            pending_order.get(
                "exchange",
                "",
            )
        ).strip()

        token = str(
            pending_order.get(
                "token",
                "",
            )
        ).strip()

        if not order_id:
            return None

        if not symbol:
            return None

        if not symbol.startswith("NIFTY"):
            return None

        if symbol.startswith("MIDCPNIFTY"):
            return None

        if exchange != "NFO":
            return None

        if not token:
            return None

        transaction_type = str(
            pending_order.get(
                "transaction_type",
                "",
            )
        ).strip().upper()

        if transaction_type != "BUY":
            return None

        try:
            quantity = int(
                pending_order.get(
                    "quantity",
                    0,
                )
            )
        except (TypeError, ValueError):
            return None

        if quantity <= 0:
            return None

        try:
            stop_loss = float(
                pending_order.get(
                    "stop_loss",
                    0.0,
                )
            )
            target_price = float(
                pending_order.get(
                    "target_price",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            return None

        if stop_loss < 0.0:
            return None

        if target_price < 0.0:
            return None

        #
        # Original decision metadata.
        #
        # These values must come from the original RUSI decision.
        # They are never generated during broker recovery.
        #
        decision_signal = str(
            pending_order.get(
                "decision_signal",
                "",
            )
        ).strip()

        if not decision_signal:
            return None

        try:
            decision_score = float(
                pending_order.get(
                    "decision_score",
                )
            )
            decision_confidence = float(
                pending_order.get(
                    "decision_confidence",
                )
            )
        except (TypeError, ValueError):
            return None

        return pending_order

    def save(
        self,
        *,
        order_id: str,
        symbol: str,
        exchange: str,
        token: str,
        transaction_type: str,
        quantity: int,
        order_type: str,
        product_type: str,
        stop_loss: float,
        target_price: float,
        decision_signal: str,
        decision_score: float,
        decision_confidence: float,
    ) -> None:
        """
        Persist one pending NIFTY Real entry order.

        No fill price or filled quantity is stored because broker
        confirmation has not yet established an actual fill.

        stop_loss and target_price are the original risk parameters
        associated with this entry.

        decision_signal, decision_score, and decision_confidence
        are copied from the original RUSI decision so that a later
        broker-fill recovery can journal the actual trade without
        inventing decision metadata.
        """

        order_id = str(order_id).strip()
        symbol = str(symbol).strip()
        exchange = str(exchange).strip().upper()
        token = str(token).strip()

        transaction_type = str(
            transaction_type
        ).strip().upper()

        order_type = str(
            order_type
        ).strip().upper()

        product_type = str(
            product_type
        ).strip().upper()

        decision_signal = str(
            decision_signal
        ).strip()

        quantity = int(quantity)
        stop_loss = float(stop_loss)
        target_price = float(target_price)
        decision_score = float(decision_score)
        decision_confidence = float(
            decision_confidence
        )

        if not order_id:
            raise ValueError(
                "Pending NIFTY order requires order_id."
            )

        if not symbol:
            raise ValueError(
                "Pending NIFTY order requires symbol."
            )

        if not symbol.startswith("NIFTY"):
            raise ValueError(
                "Pending NIFTY order symbol must start with NIFTY."
            )

        if symbol.startswith("MIDCPNIFTY"):
            raise ValueError(
                "MIDCPNIFTY cannot be stored as a NIFTY pending order."
            )

        if exchange != "NFO":
            raise ValueError(
                "Pending NIFTY order exchange must be NFO."
            )

        if not token:
            raise ValueError(
                "Pending NIFTY order requires token."
            )

        if transaction_type != "BUY":
            raise ValueError(
                "NIFTY Real entry must use BUY transaction type."
            )

        if quantity <= 0:
            raise ValueError(
                "Pending NIFTY order quantity must be positive."
            )

        if stop_loss < 0.0:
            raise ValueError(
                "Pending NIFTY order stop_loss cannot be negative."
            )

        if target_price < 0.0:
            raise ValueError(
                "Pending NIFTY order target_price cannot be negative."
            )

        if not decision_signal:
            raise ValueError(
                "Pending NIFTY order requires decision_signal."
            )

        payload = {
            "version": 3,
            "pending_order": {
                "order_id": order_id,
                "symbol": symbol,
                "exchange": exchange,
                "token": token,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "order_type": order_type,
                "product_type": product_type,
                "stop_loss": stop_loss,
                "target_price": target_price,
                "decision_signal": decision_signal,
                "decision_score": decision_score,
                "decision_confidence": decision_confidence,
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        }

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = self._path.with_suffix(
            self._path.suffix + ".tmp"
        )

        with temp_path.open(
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(
                payload,
                fp,
                indent=2,
                sort_keys=True,
            )
            fp.write("\n")
            fp.flush()
            os.fsync(fp.fileno())

        os.replace(
            temp_path,
            self._path,
        )

    def clear(self) -> None:
        """
        Remove the pending-order state.

        Safe to call when no state exists.
        """

        try:
            self._path.unlink()
        except FileNotFoundError:
            pass
