"""
Persistent live-position state.

This file is intentionally separate from the trade journal.

TradeJournal:
    Historical audit record.

PositionPersistence:
    Recovery state for positions that are still OPEN.
"""

import json
import os
from dataclasses import asdict, fields
from datetime import datetime
from enum import Enum

from common.logger import get_logger

from execution.position_manager.position import Position
from execution.position_manager.position_status import PositionStatus


logger = get_logger("RUSI")


class PositionPersistence:

    def __init__(
        self,
        market_name,
        path=None,
    ):
        self.market_name = str(market_name)

        if path is None:
            safe_market_name = (
                self.market_name
                .replace("/", "_")
                .replace(" ", "_")
            )

            path = (
                f"runs/runtime/"
                f"{safe_market_name}_open_positions.json"
            )

        self.path = path

    # =========================================================
    # SERIALIZATION
    # =========================================================

    def _serialize_value(self, value):

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Enum):
            return value.value

        return value

    def _serialize_position(self, position):

        data = {}

        for field in fields(position):

            value = getattr(
                position,
                field.name,
            )

            data[field.name] = (
                self._serialize_value(value)
            )

        return data

    # =========================================================
    # LOAD
    # =========================================================

    def _load(self):

        if not os.path.exists(self.path):
            return []

        try:

            with open(
                self.path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):
                return []

            return data

        except Exception as exc:

            logger.exception(
                "Position Persistence Load Failed | Error=%s",
                exc,
            )

            return []

    # =========================================================
    # SAVE
    # =========================================================

    def save(self, positions):

        records = []

        for position in positions:

            if position.status != PositionStatus.OPEN:
                continue

            records.append(
                {
                    "market": self.market_name,
                    "position": self._serialize_position(
                        position
                    ),
                }
            )

        # No OPEN positions remain.
        # Remove the recovery file so stale state
        # can never be mistaken for a live position.
        if not records:
            try:
                if os.path.exists(self.path):
                    os.remove(self.path)

                    logger.info(
                        "OPEN Position State Cleared | "
                        "Market=%s",
                        self.market_name,
                    )

            except Exception as exc:
                logger.exception(
                    "Position Persistence Cleanup Failed | "
                    "Error=%s",
                    exc,
                )

            return

        directory = os.path.dirname(self.path)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True,
            )

        temporary_path = (
            self.path + ".tmp"
        )

        try:

            with open(
                temporary_path,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    records,
                    file,
                    indent=2,
                )

                file.flush()
                os.fsync(file.fileno())

            os.replace(
                temporary_path,
                self.path,
            )

            logger.info(
                "OPEN Position State Persisted | "
                "Market=%s | Positions=%d",
                self.market_name,
                len(records),
            )

        except Exception as exc:

            logger.exception(
                "Position Persistence Save Failed | Error=%s",
                exc,
            )

            try:

                if os.path.exists(
                    temporary_path
                ):
                    os.remove(
                        temporary_path
                    )

            except Exception:
                pass

    # =========================================================
    # RESTORE
    # =========================================================

    def restore(self):

        records = self._load()

        restored = []

        for record in records:

            if record.get("market") != self.market_name:
                continue

            data = record.get(
                "position",
                {},
            )

            try:

                position_id = data["position_id"]

                if not data.get("symbol"):
                    continue

                entry_time = datetime.fromisoformat(
                    data["entry_time"]
                )

                exit_time = None

                if data.get("exit_time"):
                    exit_time = datetime.fromisoformat(
                        data["exit_time"]
                    )

                position = Position(

                    position_id=position_id,

                    order_id=data.get(
                        "order_id",
                        "",
                    ),

                    symbol=data["symbol"],

                    exchange=data.get(
                        "exchange",
                        "",
                    ),

                    token=str(
                        data.get(
                            "token",
                            "",
                        )
                    ),

                    transaction_type=data.get(
                        "transaction_type",
                        "BUY",
                    ),

                    quantity=int(
                        data.get(
                            "quantity",
                            0,
                        )
                    ),

                    entry_price=float(
                        data.get(
                            "entry_price",
                            0.0,
                        )
                    ),

                    current_price=float(
                        data.get(
                            "current_price",
                            0.0,
                        )
                    ),

                    highest_price=float(
                        data.get(
                            "highest_price",
                            0.0,
                        )
                    ),

                    highest_unrealized_pnl=float(
                        data.get(
                            "highest_unrealized_pnl",
                            0.0,
                        )
                    ),

                    profit_protection_active=bool(
                        data.get(
                            "profit_protection_active",
                            False,
                        )
                    ),

                    protected_price=float(
                        data.get(
                            "protected_price",
                            0.0,
                        )
                    ),

                    reversal_count=int(
                        data.get(
                            "reversal_count",
                            0,
                        )
                    ),

                    last_reversal_signal=data.get(
                        "last_reversal_signal",
                        "",
                    ),

                    stop_loss=float(
                        data.get(
                            "stop_loss",
                            0.0,
                        )
                    ),

                    target_price=float(
                        data.get(
                            "target_price",
                            0.0,
                        )
                    ),

                    unrealized_pnl=float(
                        data.get(
                            "unrealized_pnl",
                            0.0,
                        )
                    ),

                    realized_pnl=float(
                        data.get(
                            "realized_pnl",
                            0.0,
                        )
                    ),

                    entry_time=entry_time,

                    exit_time=exit_time,

                    exit_reason=data.get(
                        "exit_reason",
                        "",
                    ),

                    status=PositionStatus(
                        data.get(
                            "status",
                            PositionStatus.OPEN.value,
                        )
                    ),
                )

                if position.status != PositionStatus.OPEN:
                    continue

                restored.append(position)

            except Exception as exc:

                logger.exception(
                    "Position Restore Failed | "
                    "Market=%s | Position=%s | Error=%s",
                    self.market_name,
                    data.get(
                        "position_id",
                        "UNKNOWN",
                    ),
                    exc,
                )

        return restored
