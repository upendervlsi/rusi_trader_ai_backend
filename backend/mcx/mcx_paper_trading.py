"""
RUSI Trader AI - MCX Paper Trading Engine.

MCX-only isolated paper trading.

Supported:
    - CRUDEOILM
    - GOLDM
    - SILVERM

Important:
    - Paper execution only.
    - No broker order placement.
    - Does not modify the existing RUSI paper engine.
    - Does not modify NIFTY, Stock Options, or Midcap.
    - Only qualified MCX intelligence may create a trade.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
STATE_FILE = BASE_DIR / "data" / "mcx" / "paper_trading.json"

SUPPORTED_KEYS = {
    "crude": "CRUDEOILM",
    "gold": "GOLDM",
    "silver": "SILVERM",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class McxPaperTradingEngine:
    """
    Isolated MCX paper portfolio.

    One active position is allowed per MCX instrument.
    """

    VERSION = 1

    def __init__(self, state_file: Path = STATE_FILE) -> None:
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.state = self._load()

    # =========================================================
    # STATE
    # =========================================================

    def _default_state(self) -> dict[str, Any]:
        return {
            "version": self.VERSION,
            "market": "MCX",
            "mode": "PAPER",
            "created_at": _now(),
            "updated_at": _now(),
            "active_positions": {},
            "closed_trades": [],
        }

    def _load(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return self._default_state()

        try:
            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as handle:
                data = json.load(handle)

            if not isinstance(data, dict):
                return self._default_state()

            data.setdefault("version", self.VERSION)
            data.setdefault("market", "MCX")
            data.setdefault("mode", "PAPER")
            data.setdefault("active_positions", {})
            data.setdefault("closed_trades", [])

            return data

        except (OSError, json.JSONDecodeError):
            return self._default_state()

    def _save(self) -> None:
        self.state["updated_at"] = _now()

        self.state_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fd, temporary_name = tempfile.mkstemp(
            prefix=".mcx_paper_",
            suffix=".tmp",
            dir=str(self.state_file.parent),
        )

        try:
            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    self.state,
                    handle,
                    indent=2,
                    ensure_ascii=False,
                )
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(
                temporary_name,
                self.state_file,
            )

        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)

    # =========================================================
    # POSITION HELPERS
    # =========================================================

    def _key_from_instrument(
        self,
        instrument: dict[str, Any],
    ) -> str | None:
        key = str(
            instrument.get("key", "")
        ).lower()

        if key in SUPPORTED_KEYS:
            return key

        symbol = str(
            instrument.get("symbol", "")
        ).upper()

        for supported_key, supported_symbol in SUPPORTED_KEYS.items():
            if symbol.startswith(supported_symbol):
                return supported_key

        return None

    def _position(
        self,
        key: str,
    ) -> dict[str, Any] | None:
        position = self.state["active_positions"].get(key)

        if isinstance(position, dict):
            return position

        return None

    # =========================================================
    # ENTRY
    # =========================================================

    def process_instrument(
        self,
        instrument: dict[str, Any],
    ) -> dict[str, Any]:
        key = self._key_from_instrument(instrument)

        if key is None:
            return {
                "action": "IGNORED",
                "reason": "UNSUPPORTED_INSTRUMENT",
            }

        symbol = SUPPORTED_KEYS[key]

        signal = str(
            instrument.get("signal", "WAIT")
        ).upper()

        qualified = instrument.get(
            "qualified",
            0,
        )

        try:
            qualified = int(qualified)
        except (TypeError, ValueError):
            qualified = 0

        # -----------------------------------------------------
        # Underlying and option prices are intentionally separate.
        #
        # Underlying price drives the intelligence risk levels.
        # Option price drives paper P&L.
        # -----------------------------------------------------
        underlying_ltp = _float(
            instrument.get("underlying_ltp")
            if instrument.get("underlying_ltp") is not None
            else instrument.get("ltp")
        )

        option_ltp = _float(
            instrument.get("option_ltp")
        )

        # For the new option-aware path, an option LTP is mandatory.
        # The legacy underlying-only path remains blocked from
        # creating a new MCX paper trade.
        ltp = option_ltp

        entry = _float(
            instrument.get("entry")
        )

        stop_loss = _float(
            instrument.get("stop_loss")
        )

        target = _float(
            instrument.get("target")
        )

        risk_reward = _float(
            instrument.get("risk_reward")
        )

        existing = self._position(key)

        # -----------------------------------------------------
        # Existing position gets monitored first.
        # -----------------------------------------------------

        if existing is not None:
            return self._monitor_position(
                key=key,
                instrument=instrument,
                position=existing,
            )

        # -----------------------------------------------------
        # WAIT never creates a trade.
        # -----------------------------------------------------

        if signal not in {"BUY", "SELL"}:
            return {
                "key": key,
                "symbol": symbol,
                "action": "WAIT",
                "signal": signal,
                "qualified": qualified,
                "reason": "SIGNAL_NOT_TRADEABLE",
            }

        # -----------------------------------------------------
        # Qualification is mandatory.
        # -----------------------------------------------------

        if qualified != 1:
            return {
                "key": key,
                "symbol": symbol,
                "action": "WAIT",
                "signal": signal,
                "qualified": qualified,
                "reason": "NOT_QUALIFIED",
            }

        # -----------------------------------------------------
        # Risk values must exist.
        # -----------------------------------------------------

        if (
            underlying_ltp is None
            or option_ltp is None
            or entry is None
            or stop_loss is None
            or target is None
        ):
            return {
                "key": key,
                "symbol": symbol,
                "action": "BLOCKED",
                "signal": signal,
                "qualified": qualified,
                "reason": "MISSING_ENTRY_RISK_DATA",
            }

        # -----------------------------------------------------
        # Prevent invalid BUY/SELL risk geometry.
        # -----------------------------------------------------

        if signal == "BUY":
            valid_geometry = (
                stop_loss < entry < target
            )
        else:
            valid_geometry = (
                target < entry < stop_loss
            )

        if not valid_geometry:
            return {
                "key": key,
                "symbol": symbol,
                "action": "BLOCKED",
                "signal": signal,
                "qualified": qualified,
                "reason": "INVALID_RISK_GEOMETRY",
            }

        # -----------------------------------------------------
        # Same candle duplicate protection.
        # -----------------------------------------------------

        candle_timestamp = (
            instrument.get("candle_timestamp")
            or instrument.get("timestamp")
            or instrument.get("last_candle")
        )

        closed_trades = self.state.get(
            "closed_trades",
            [],
        )

        for trade in closed_trades:
            if not isinstance(trade, dict):
                continue

            if (
                trade.get("key") == key
                and trade.get("entry_candle_timestamp")
                == candle_timestamp
            ):
                return {
                    "key": key,
                    "symbol": symbol,
                    "action": "DUPLICATE_BLOCKED",
                    "reason": "CANDLE_ALREADY_TRADED",
                }

        # -----------------------------------------------------
        # Create paper position.
        # -----------------------------------------------------

        trade_id = str(uuid.uuid4())

        # -----------------------------------------------------
        # Option contract metadata is mandatory for the new
        # MCX option paper path.
        # -----------------------------------------------------
        trade_symbol = instrument.get("trade_symbol")
        option_type = instrument.get("option_type")
        strike = _float(instrument.get("strike"))
        expiry = instrument.get("expiry")
        option_token = instrument.get("option_token")
        lot_size = instrument.get("lot_size")

        if not all(
            [
                trade_symbol,
                option_type in {"CE", "PE"},
                strike is not None,
                expiry,
                option_token,
                lot_size,
            ]
        ):
            return {
                "key": key,
                "symbol": symbol,
                "action": "BLOCKED",
                "signal": signal,
                "qualified": qualified,
                "reason": "OPTION_CONTRACT_DATA_MISSING",
            }

        try:
            lot_size = int(lot_size)
        except (TypeError, ValueError):
            return {
                "key": key,
                "symbol": symbol,
                "action": "BLOCKED",
                "signal": signal,
                "qualified": qualified,
                "reason": "INVALID_OPTION_LOT_SIZE",
            }

        if lot_size <= 0:
            return {
                "key": key,
                "symbol": symbol,
                "action": "BLOCKED",
                "signal": signal,
                "qualified": qualified,
                "reason": "INVALID_OPTION_LOT_SIZE",
            }

        # Intelligence quantity is not reused for the option
        # contract. The selector's lot size is authoritative.
        quantity = lot_size

        position = {
            "trade_id": trade_id,
            "market": "MCX",
            "mode": "PAPER",
            "key": key,

            # Analysis / underlying identity.
            "symbol": symbol,
            "analysis_symbol": instrument.get(
                "analysis_symbol",
                symbol,
            ),
            "resolved_symbol": instrument.get(
                "resolved_symbol"
            ),

            # Actual executable option contract identity.
            "trade_symbol": str(trade_symbol),
            "option_type": str(option_type),
            "strike": strike,
            "expiry": str(expiry),
            "option_token": str(option_token),
            "lot_size": quantity,

            "direction": signal,

            # Underlying intelligence risk model.
            "underlying_entry": entry,
            "underlying_stop_loss": stop_loss,
            "underlying_target": target,
            "risk_reward": risk_reward,

            # Actual option paper execution price.
            "entry_price": option_ltp,
            "entry_ltp": option_ltp,
            "underlying_entry_ltp": underlying_ltp,

            "quantity": quantity,
            "entry_time": _now(),
            "entry_candle_timestamp": candle_timestamp,
            "confidence": _float(
                instrument.get("confidence")
            ),
            "trend": instrument.get("trend"),
            "momentum": instrument.get("momentum"),
            "structure": instrument.get("structure"),
            "status": "ACTIVE",

            # Option price is used for P&L.
            "last_ltp": option_ltp,
            "option_entry_ltp": option_ltp,
            "option_last_ltp": option_ltp,
            "underlying_last_ltp": underlying_ltp,

            "unrealized_pnl": 0.0,
        }

        self.state["active_positions"][key] = position
        self._save()

        return {
            "key": key,
            "symbol": symbol,
            "analysis_symbol": position["analysis_symbol"],
            "resolved_symbol": position["resolved_symbol"],
            "trade_symbol": position["trade_symbol"],
            "option_type": position["option_type"],
            "strike": position["strike"],
            "expiry": position["expiry"],
            "option_token": position["option_token"],
            "lot_size": position["lot_size"],
            "action": "PAPER_ENTRY",
            "status": "ACTIVE",
            "trade_id": trade_id,
            "direction": signal,
            "underlying_entry": position["underlying_entry"],
            "underlying_stop_loss": position["underlying_stop_loss"],
            "underlying_target": position["underlying_target"],
            "option_entry_price": position["entry_price"],
            "quantity": position["quantity"],
        }

    # =========================================================
    # MONITOR
    # =========================================================

    def _monitor_position(
        self,
        key: str,
        instrument: dict[str, Any],
        position: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Monitor an active MCX option paper position.

        Price responsibilities are deliberately separated:

            Underlying LTP
                -> SL / Target exit decision

            Option LTP
                -> Paper P&L

        The saved option contract is authoritative for the
        active position. The runner must not replace it with
        another strike or expiry.
        """

        underlying_ltp = _float(
            instrument.get("underlying_ltp")
            if instrument.get("underlying_ltp") is not None
            else instrument.get("ltp")
        )

        option_ltp = _float(
            instrument.get("option_ltp")
        )

        if underlying_ltp is None:
            return {
                "key": key,
                "symbol": position["symbol"],
                "action": "MONITOR_BLOCKED",
                "reason": "NO_UNDERLYING_LTP",
                "trade_id": position["trade_id"],
            }

        if option_ltp is None:
            return {
                "key": key,
                "symbol": position["symbol"],
                "action": "MONITOR_BLOCKED",
                "reason": "NO_OPTION_LTP",
                "trade_id": position["trade_id"],
            }

        direction = str(
            position.get("direction", "")
        ).upper()

        entry_option = _float(
            position.get("entry_price")
        )

        underlying_stop_loss = _float(
            position.get("underlying_stop_loss")
        )

        underlying_target = _float(
            position.get("underlying_target")
        )

        if entry_option is None:
            return {
                "key": key,
                "symbol": position["symbol"],
                "action": "MONITOR_BLOCKED",
                "reason": "INVALID_OPTION_ENTRY_PRICE",
                "trade_id": position["trade_id"],
            }

        if underlying_stop_loss is None:
            return {
                "key": key,
                "symbol": position["symbol"],
                "action": "MONITOR_BLOCKED",
                "reason": "UNDERLYING_STOP_LOSS_MISSING",
                "trade_id": position["trade_id"],
            }

        if underlying_target is None:
            return {
                "key": key,
                "symbol": position["symbol"],
                "action": "MONITOR_BLOCKED",
                "reason": "UNDERLYING_TARGET_MISSING",
                "trade_id": position["trade_id"],
            }

        quantity = position.get(
            "quantity",
            1,
        )

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            quantity = 1.0

        if quantity <= 0:
            return {
                "key": key,
                "symbol": position["symbol"],
                "action": "MONITOR_BLOCKED",
                "reason": "INVALID_QUANTITY",
                "trade_id": position["trade_id"],
            }

        # -----------------------------------------------------
        # Option price is used ONLY for P&L.
        # -----------------------------------------------------

        option_price = option_ltp

        if direction == "BUY":
            pnl = (
                option_price - entry_option
            ) * quantity
        elif direction == "SELL":
            pnl = (
                entry_option - option_price
            ) * quantity
        else:
            return {
                "key": key,
                "symbol": position["symbol"],
                "action": "MONITOR_BLOCKED",
                "reason": "INVALID_DIRECTION",
                "trade_id": position["trade_id"],
            }

        position["last_ltp"] = option_price
        position["option_last_ltp"] = option_price
        position["underlying_last_ltp"] = underlying_ltp
        position["unrealized_pnl"] = pnl

        # -----------------------------------------------------
        # Exit conditions use UNDERLYING price.
        #
        # We deliberately do NOT compare option premium against
        # underlying SL/target.
        # -----------------------------------------------------

        exit_reason = None
        exit_underlying_price = None

        if direction == "BUY":
            if underlying_ltp <= underlying_stop_loss:
                exit_reason = "STOP_LOSS"
                exit_underlying_price = underlying_stop_loss

            elif underlying_ltp >= underlying_target:
                exit_reason = "TARGET"
                exit_underlying_price = underlying_target

        else:
            if underlying_ltp >= underlying_stop_loss:
                exit_reason = "STOP_LOSS"
                exit_underlying_price = underlying_stop_loss

            elif underlying_ltp <= underlying_target:
                exit_reason = "TARGET"
                exit_underlying_price = underlying_target

        # -----------------------------------------------------
        # Position remains active.
        # -----------------------------------------------------

        if exit_reason is None:
            self._save()

            return {
                "key": key,
                "symbol": position["symbol"],
                "trade_symbol": position.get(
                    "trade_symbol"
                ),
                "option_type": position.get(
                    "option_type"
                ),
                "strike": position.get(
                    "strike"
                ),
                "expiry": position.get(
                    "expiry"
                ),
                "action": "MONITOR",
                "status": "ACTIVE",
                "trade_id": position["trade_id"],
                "underlying_ltp": underlying_ltp,
                "option_ltp": option_price,
                "unrealized_pnl": pnl,
            }

        # -----------------------------------------------------
        # Close paper position.
        #
        # P&L uses the ACTUAL OBSERVED OPTION LTP.
        #
        # The underlying SL/target level is recorded separately
        # as the trigger level.
        # -----------------------------------------------------

        if direction == "BUY":
            realized_pnl = (
                option_price - entry_option
            ) * quantity
        else:
            realized_pnl = (
                entry_option - option_price
            ) * quantity

        position["exit_price"] = option_price
        position["exit_ltp"] = option_price
        position["exit_option_ltp"] = option_price
        position["exit_underlying_price"] = underlying_ltp
        position["exit_trigger_price"] = (
            exit_underlying_price
        )
        position["exit_time"] = _now()
        position["exit_reason"] = exit_reason
        position["realized_pnl"] = realized_pnl
        position["unrealized_pnl"] = 0.0
        position["status"] = "CLOSED"

        self.state["closed_trades"].append(position)

        self.state["active_positions"].pop(
            key,
            None,
        )

        self._save()

        return {
            "key": key,
            "symbol": position["symbol"],
            "trade_symbol": position.get(
                "trade_symbol"
            ),
            "option_type": position.get(
                "option_type"
            ),
            "strike": position.get(
                "strike"
            ),
            "expiry": position.get(
                "expiry"
            ),
            "action": "PAPER_EXIT",
            "status": "CLOSED",
            "trade_id": position["trade_id"],
            "exit_reason": exit_reason,
            "underlying_ltp": underlying_ltp,
            "exit_underlying_price": underlying_ltp,
            "exit_trigger_price": exit_underlying_price,
            "option_ltp": option_price,
            "exit_option_ltp": option_price,
            "realized_pnl": realized_pnl,
        }

    # =========================================================
    # PORTFOLIO SNAPSHOT
    # =========================================================

    def snapshot(self) -> dict[str, Any]:
        active = self.state.get(
            "active_positions",
            {},
        )

        closed = self.state.get(
            "closed_trades",
            [],
        )

        realized_pnl = 0.0

        for trade in closed:
            if isinstance(trade, dict):
                value = _float(
                    trade.get("realized_pnl")
                )

                if value is not None:
                    realized_pnl += value

        unrealized_pnl = 0.0

        for position in active.values():
            if isinstance(position, dict):
                value = _float(
                    position.get("unrealized_pnl")
                )

                if value is not None:
                    unrealized_pnl += value

        return {
            "market": "MCX",
            "mode": "PAPER",
            "running": True,
            "active_positions": len(active),
            "closed_trades": len(closed),
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "positions": list(active.values()),
            "updated_at": self.state.get(
                "updated_at"
            ),
        }
