"""
RUSI Trader AI - MCX Paper Trading Runner.

One complete MCX paper-trading cycle.

Pipeline:

    MCX live market/intelligence
        ->
    MCX latest candle timestamp
        ->
    Existing active position?
        ->
        YES -> resolve saved option contract
             -> fetch same option LTP
             -> monitor / exit

        NO  -> BUY/SELL + qualified=1?
             ->
             MCX Option Selector
             ->
             actual CE/PE contract
             ->
             actual option LTP
             ->
             MCX paper engine
             ->
             PAPER ENTRY

No real broker order is submitted.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.mcx.mcx_service import McxService
from backend.mcx.mcx_option_selector import McxOptionSelector
from backend.mcx.mcx_paper_trading import (
    McxPaperTradingEngine,
)


SUPPORTED_KEYS = (
    "crude",
    "gold",
    "silver",
)


def _instrument_map(
    response: dict,
) -> dict[str, dict]:
    result: dict[str, dict] = {}

    instruments = response.get(
        "instruments"
    )

    if not isinstance(instruments, list):
        return result

    for instrument in instruments:
        if not isinstance(instrument, dict):
            continue

        key = str(
            instrument.get("key", "")
        ).lower()

        if key in SUPPORTED_KEYS:
            result[key] = instrument

    return result


def _latest_candle_timestamp(
    service: McxService,
    key: str,
) -> str | None:
    candles = service.get_candles(key)

    if not isinstance(candles, list):
        return None

    if not candles:
        return None

    latest = candles[-1]

    if not isinstance(latest, list):
        return None

    if not latest:
        return None

    timestamp = latest[0]

    if timestamp is None:
        return None

    return str(timestamp)


def _float(
    value: Any,
) -> float | None:
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def _active_position(
    snapshot: dict,
    key: str,
) -> dict[str, Any] | None:
    active = snapshot.get(
        "active_positions",
        {},
    )

    if not isinstance(active, dict):
        return None

    position = active.get(key)

    if not isinstance(position, dict):
        return None

    return position


def _prepare_existing_position(
    service: McxService,
    instrument: dict[str, Any],
    position: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare an existing option position for monitoring.

    The saved option contract is authoritative.

    We deliberately do NOT call the option selector here.
    """

    trade_symbol = str(
        position.get("trade_symbol", "")
    ).strip()

    option_token = str(
        position.get("option_token", "")
    ).strip()

    exchange = str(
        position.get("option_exchange")
        or "MCX"
    ).strip().upper()

    if not trade_symbol:
        return {
            "error": "ACTIVE_POSITION_MISSING_TRADE_SYMBOL",
        }

    if not option_token:
        return {
            "error": "ACTIVE_POSITION_MISSING_OPTION_TOKEN",
        }

    option_response = service._market_data.get_option_ltp(
        exchange=exchange,
        symbol=trade_symbol,
        token=option_token,
    )

    if not isinstance(option_response, dict):
        return {
            "error": "OPTION_LTP_RESPONSE_INVALID",
        }

    if option_response.get("status") is not True:
        return {
            "error": (
                "OPTION_LTP_REQUEST_FAILED:"
                f"{option_response.get('message', 'UNKNOWN')}"
            ),
        }

    data = option_response.get("data")

    if not isinstance(data, dict):
        return {
            "error": "OPTION_LTP_DATA_MISSING",
        }

    option_ltp = _float(
        data.get("ltp")
    )

    if option_ltp is None:
        return {
            "error": "OPTION_LTP_MISSING",
        }

    instrument["underlying_ltp"] = _float(
        instrument.get("ltp")
    )

    instrument["option_ltp"] = option_ltp

    instrument["trade_symbol"] = trade_symbol
    instrument["option_type"] = position.get(
        "option_type"
    )
    instrument["strike"] = position.get(
        "strike"
    )
    instrument["expiry"] = position.get(
        "expiry"
    )
    instrument["option_token"] = option_token
    instrument["option_exchange"] = exchange
    instrument["lot_size"] = position.get(
        "lot_size",
        position.get("quantity"),
    )

    return {
        "option_ltp": option_ltp,
        "trade_symbol": trade_symbol,
    }


def _prepare_new_entry(
    service: McxService,
    selector: McxOptionSelector,
    instrument: dict[str, Any],
) -> dict[str, Any]:
    """
    Resolve one actual option contract for a NEW paper entry.

    Option selection occurs only after BUY/SELL + qualification.
    """

    signal = str(
        instrument.get("signal", "WAIT")
    ).upper()

    try:
        qualified = int(
            instrument.get("qualified", 0)
        )
    except (TypeError, ValueError):
        qualified = 0

    if signal not in {"BUY", "SELL"}:
        return {
            "error": "SIGNAL_NOT_TRADEABLE",
        }

    if qualified != 1:
        return {
            "error": "NOT_QUALIFIED",
        }

    analysis_symbol = str(
        instrument.get(
            "analysis_symbol"
        )
        or instrument.get("symbol", "")
    ).strip().upper()

    underlying_ltp = _float(
        instrument.get("ltp")
    )

    if not analysis_symbol:
        return {
            "error": "ANALYSIS_SYMBOL_MISSING",
        }

    if underlying_ltp is None:
        return {
            "error": "UNDERLYING_LTP_MISSING",
        }

    selection = selector.select(
        analysis_symbol=analysis_symbol,
        signal=signal,
        qualified=qualified,
        underlying_price=underlying_ltp,
    )

    if selection is None:
        return {
            "error": "OPTION_SELECTION_FAILED",
        }

    option_response = service._market_data.get_option_ltp(
        exchange=selection.exchange,
        symbol=selection.trade_symbol,
        token=str(selection.token),
    )

    if not isinstance(option_response, dict):
        return {
            "error": "OPTION_LTP_RESPONSE_INVALID",
        }

    if option_response.get("status") is not True:
        return {
            "error": (
                "OPTION_LTP_REQUEST_FAILED:"
                f"{option_response.get('message', 'UNKNOWN')}"
            ),
        }

    data = option_response.get("data")

    if not isinstance(data, dict):
        return {
            "error": "OPTION_LTP_DATA_MISSING",
        }

    option_ltp = _float(
        data.get("ltp")
    )

    if option_ltp is None:
        return {
            "error": "OPTION_LTP_MISSING",
        }

    instrument["underlying_ltp"] = underlying_ltp
    instrument["option_ltp"] = option_ltp

    instrument["analysis_symbol"] = (
        selection.analysis_symbol
    )
    instrument["trade_symbol"] = (
        selection.trade_symbol
    )
    instrument["option_type"] = (
        selection.option_type
    )
    instrument["strike"] = (
        selection.strike
    )
    instrument["expiry"] = (
        selection.expiry
    )
    instrument["option_token"] = str(
        selection.token
    )
    instrument["option_exchange"] = (
        selection.exchange
    )
    instrument["lot_size"] = (
        selection.lot_size
    )

    return {
        "option_ltp": option_ltp,
        "trade_symbol": selection.trade_symbol,
        "option_type": selection.option_type,
        "strike": selection.strike,
        "expiry": selection.expiry,
        "option_token": str(selection.token),
        "lot_size": selection.lot_size,
    }


def run_paper_cycle() -> dict:
    started = datetime.now().isoformat(
        timespec="seconds"
    )

    print()
    print("=" * 80)
    print("RUSI MCX PAPER TRADING CYCLE")
    print("=" * 80)
    print("Started :", started)
    print("Mode    : PAPER ONLY")
    print("Markets : CRUDEOILM / GOLDM / SILVERM")
    print("Execution: PAPER ONLY - NO REAL ORDERS")
    print("=" * 80)

    service = McxService()
    selector = McxOptionSelector()
    engine = McxPaperTradingEngine()

    response = service.get_intelligence()

    if not isinstance(response, dict):
        raise RuntimeError(
            "MCX intelligence response is not a dictionary"
        )

    instruments = _instrument_map(response)

    # Take the snapshot before processing so we know which
    # instruments already have active positions.
    initial_snapshot = engine.snapshot()

    results = []

    for key in SUPPORTED_KEYS:
        instrument = instruments.get(key)

        if instrument is None:
            results.append(
                {
                    "key": key,
                    "action": "BLOCKED",
                    "reason": "INSTRUMENT_DATA_MISSING",
                }
            )
            continue

        candle_timestamp = _latest_candle_timestamp(
            service,
            key,
        )

        if candle_timestamp is not None:
            instrument["entry_candle_timestamp"] = (
                candle_timestamp
            )

        existing = _active_position(
            initial_snapshot,
            key,
        )

        # -----------------------------------------------------
        # Existing position:
        # use the SAME saved option contract.
        # -----------------------------------------------------
        if existing is not None:
            prepared = _prepare_existing_position(
                service=service,
                instrument=instrument,
                position=existing,
            )

            if "error" in prepared:
                result = {
                    "key": key,
                    "action": "BLOCKED",
                    "reason": prepared["error"],
                }

                results.append(result)

                print()
                print(
                    f"[MCX PAPER] {key.upper()}"
                )
                print(
                    "  position   : ACTIVE"
                )
                print(
                    "  trade      :",
                    existing.get("trade_symbol"),
                )
                print(
                    "  action     : BLOCKED"
                )
                print(
                    "  reason     :",
                    prepared["error"],
                )

                continue

            print()
            print(
                f"[MCX PAPER] {key.upper()}"
            )
            print(
                "  position   : ACTIVE"
            )
            print(
                "  trade      :",
                prepared["trade_symbol"],
            )
            print(
                "  option LTP :",
                prepared["option_ltp"],
            )
            print(
                "  underlying :",
                instrument.get("underlying_ltp"),
            )

        # -----------------------------------------------------
        # New position:
        # resolve option only after qualification.
        # -----------------------------------------------------
        else:
            prepared = _prepare_new_entry(
                service=service,
                selector=selector,
                instrument=instrument,
            )

            if "error" in prepared:
                # WAIT and non-qualified signals are expected
                # and should remain normal non-trade outcomes.
                result = engine.process_instrument(
                    instrument
                )

                results.append(result)

                print()
                print(
                    f"[MCX PAPER] {key.upper()}"
                )
                print(
                    "  signal     :",
                    instrument.get("signal"),
                )
                print(
                    "  qualified  :",
                    instrument.get("qualified"),
                )
                print(
                    "  underlying :",
                    instrument.get("ltp"),
                )
                print(
                    "  action     :",
                    result.get("action"),
                )
                print(
                    "  reason     :",
                    result.get("reason"),
                )

                continue

        # -----------------------------------------------------
        # Paper engine now receives:
        #
        #   underlying_ltp
        #   option_ltp
        #   actual option contract metadata
        #
        # Existing risk/qualification/duplicate protections
        # remain inside the paper engine.
        # -----------------------------------------------------
        result = engine.process_instrument(
            instrument
        )

        results.append(result)

        print()
        print(
            f"[MCX PAPER] {key.upper()}"
        )
        print(
            "  signal     :",
            instrument.get("signal"),
        )
        print(
            "  qualified  :",
            instrument.get("qualified"),
        )
        print(
            "  underlying :",
            instrument.get("underlying_ltp"),
        )
        print(
            "  option LTP :",
            instrument.get("option_ltp"),
        )
        print(
            "  trade      :",
            instrument.get("trade_symbol"),
        )
        print(
            "  option     :",
            instrument.get("option_type"),
        )
        print(
            "  strike     :",
            instrument.get("strike"),
        )
        print(
            "  expiry     :",
            instrument.get("expiry"),
        )
        print(
            "  candle     :",
            instrument.get(
                "entry_candle_timestamp"
            ),
        )
        print(
            "  action     :",
            result.get("action"),
        )

        if "trade_id" in result:
            print(
                "  trade_id   :",
                result["trade_id"],
            )

        if "realized_pnl" in result:
            print(
                "  realized   :",
                result["realized_pnl"],
            )

    snapshot = engine.snapshot()

    print()
    print("=" * 80)
    print("MCX PAPER PORTFOLIO")
    print("=" * 80)
    print(
        "Active positions :",
        snapshot["active_positions"],
    )
    print(
        "Closed trades    :",
        snapshot["closed_trades"],
    )
    print(
        "Realized P&L     :",
        snapshot["realized_pnl"],
    )
    print(
        "Unrealized P&L   :",
        snapshot["unrealized_pnl"],
    )
    print("=" * 80)

    return {
        "started": started,
        "results": results,
        "portfolio": snapshot,
    }


if __name__ == "__main__":
    run_paper_cycle()
