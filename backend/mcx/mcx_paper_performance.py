"""
RUSI Trader AI - MCX Paper Trading Performance.

Read-only performance/observability layer.

Important:
    - Reads MCX paper state only.
    - Does not create trades.
    - Does not modify trades.
    - Does not submit broker orders.
    - Does not modify MCX intelligence.
    - Does not modify NIFTY, Stock Options, or Midcap.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]

PAPER_STATE_FILE = (
    BASE_DIR
    / "data"
    / "mcx"
    / "paper_trading.json"
)

OBSERVATION_FILE = (
    BASE_DIR
    / "data"
    / "mcx"
    / "intelligence_observations.jsonl"
)

SUPPORTED_SYMBOLS = {
    "CRUDEOILM",
    "GOLDM",
    "SILVERM",
}


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [
            item
            for item in value
            if isinstance(item, dict)
        ]

    if isinstance(value, dict):
        return [
            item
            for item in value.values()
            if isinstance(item, dict)
        ]

    return []


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        return data if isinstance(data, dict) else {}

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {}


def _load_observations() -> list[dict[str, Any]]:
    if not OBSERVATION_FILE.exists():
        return []

    records: list[dict[str, Any]] = []

    try:
        with OBSERVATION_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:
                line = line.strip()

                if not line:
                    continue

                try:
                    value = json.loads(line)

                    if isinstance(value, dict):
                        records.append(value)

                except json.JSONDecodeError:
                    continue

    except OSError:
        return []

    return records


def _market_symbol(trade: dict[str, Any]) -> str:
    symbol = str(
        trade.get("analysis_symbol")
        or trade.get("symbol")
        or trade.get("key")
        or ""
    ).upper()

    if symbol in SUPPORTED_SYMBOLS:
        return symbol

    key = str(
        trade.get("key") or ""
    ).lower()

    return {
        "crude": "CRUDEOILM",
        "gold": "GOLDM",
        "silver": "SILVERM",
    }.get(key, symbol)


def _build_trade_view(
    trade: dict[str, Any],
) -> dict[str, Any]:

    return {
        "trade_id": trade.get("trade_id"),
        "market": "MCX",

        "analysis_symbol": (
            trade.get("analysis_symbol")
            or _market_symbol(trade)
        ),

        "trade_symbol": trade.get(
            "trade_symbol"
        ),

        "resolved_symbol": trade.get(
            "resolved_symbol"
        ),

        "direction": trade.get(
            "direction"
        ),

        "option_type": trade.get(
            "option_type"
        ),

        "strike": trade.get(
            "strike"
        ),

        "expiry": trade.get(
            "expiry"
        ),

        "option_token": trade.get(
            "option_token"
        ),

        "quantity": trade.get(
            "quantity"
        ),

        "entry_price": trade.get(
            "entry_price"
        ),

        "entry_option_ltp": trade.get(
            "entry_option_ltp",
            trade.get("entry_price"),
        ),

        "option_last_ltp": trade.get(
            "option_last_ltp",
            trade.get("last_ltp"),
        ),

        "underlying_entry": trade.get(
            "underlying_entry"
        ),

        "underlying_last_ltp": trade.get(
            "underlying_last_ltp"
        ),

        "underlying_stop_loss": trade.get(
            "underlying_stop_loss",
            trade.get("stop_loss"),
        ),

        "underlying_target": trade.get(
            "underlying_target",
            trade.get("target"),
        ),

        "exit_price": trade.get(
            "exit_price"
        ),

        "exit_option_ltp": trade.get(
            "exit_option_ltp",
            trade.get("exit_price"),
        ),

        "exit_underlying_price": trade.get(
            "exit_underlying_price"
        ),

        "entry_time": trade.get(
            "entry_time"
        ),

        "exit_time": trade.get(
            "exit_time"
        ),

        "exit_reason": trade.get(
            "exit_reason"
        ),

        "status": trade.get(
            "status"
        ),

        "confidence": trade.get(
            "confidence"
        ),

        "risk_reward": trade.get(
            "risk_reward"
        ),

        "realized_pnl": _float(
            trade.get("realized_pnl")
        ),

        "unrealized_pnl": _float(
            trade.get("unrealized_pnl")
        ),
    }


def _observation_metrics(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:

    signal_count = 0
    qualified_count = 0

    signal_by_symbol = defaultdict(int)
    qualified_by_symbol = defaultdict(int)

    for record in observations:

        intelligence = record.get(
            "intelligence"
        )

        if not isinstance(
            intelligence,
            dict,
        ):
            continue

        signal = str(
            intelligence.get("signal")
            or "WAIT"
        ).upper()

        qualified = intelligence.get(
            "qualified"
        )

        market = record.get(
            "market"
        )

        if not isinstance(
            market,
            dict,
        ):
            market = {}

        symbol = str(
            market.get("instrument")
            or market.get("symbol")
            or ""
        ).upper()

        if signal in {
            "BUY",
            "SELL",
        }:
            signal_count += 1

            if symbol:
                signal_by_symbol[symbol] += 1

        try:
            is_qualified = (
                int(qualified) == 1
            )
        except (
            TypeError,
            ValueError,
        ):
            is_qualified = False

        if is_qualified:
            qualified_count += 1

            if symbol:
                qualified_by_symbol[symbol] += 1

    return {
        "observations": len(observations),
        "signals_generated": signal_count,
        "qualified_signals": qualified_count,
        "signal_by_symbol": dict(
            signal_by_symbol
        ),
        "qualified_by_symbol": dict(
            qualified_by_symbol
        ),
    }


def build_performance() -> dict[str, Any]:

    state = _load_json(
        PAPER_STATE_FILE
    )

    active_raw = state.get(
        "active_positions",
        {},
    )

    closed_raw = state.get(
        "closed_trades",
        [],
    )

    active = _list(active_raw)
    closed = _list(closed_raw)

    active_views = [
        _build_trade_view(item)
        for item in active
    ]

    closed_views = [
        _build_trade_view(item)
        for item in closed
    ]

    all_trades = (
        closed_views
        + active_views
    )

    wins = [
        trade
        for trade in closed_views
        if trade["realized_pnl"] > 0
    ]

    losses = [
        trade
        for trade in closed_views
        if trade["realized_pnl"] < 0
    ]

    gross_profit = sum(
        trade["realized_pnl"]
        for trade in wins
    )

    gross_loss = sum(
        trade["realized_pnl"]
        for trade in losses
    )

    realized_pnl = sum(
        trade["realized_pnl"]
        for trade in closed_views
    )

    unrealized_pnl = sum(
        trade["unrealized_pnl"]
        for trade in active_views
    )

    total_closed = len(closed_views)
    total_trades = (
        total_closed
        + len(active_views)
    )

    win_rate = (
        (len(wins) / total_closed) * 100.0
        if total_closed
        else 0.0
    )

    average_trade = (
        realized_pnl / total_closed
        if total_closed
        else 0.0
    )

    # ---------------------------------------------------------
    # Drawdown / equity curve
    # ---------------------------------------------------------

    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0

    equity_curve: list[dict[str, Any]] = []

    ordered_closed = sorted(
        closed_views,
        key=lambda item: str(
            item.get("exit_time")
            or item.get("entry_time")
            or ""
        ),
    )

    for trade in ordered_closed:

        equity += trade[
            "realized_pnl"
        ]

        peak = max(
            peak,
            equity,
        )

        drawdown = equity - peak

        max_drawdown = min(
            max_drawdown,
            drawdown,
        )

        equity_curve.append(
            {
                "time": (
                    trade.get("exit_time")
                    or trade.get("entry_time")
                ),
                "pnl": trade[
                    "realized_pnl"
                ],
                "cumulative_pnl": equity,
                "drawdown": drawdown,
            }
        )

    # ---------------------------------------------------------
    # Exit analysis
    # ---------------------------------------------------------

    target_exits = sum(
        1
        for trade in closed_views
        if str(
            trade.get("exit_reason")
            or ""
        ).upper()
        == "TARGET"
    )

    stop_exits = sum(
        1
        for trade in closed_views
        if str(
            trade.get("exit_reason")
            or ""
        ).upper()
        in {
            "STOP_LOSS",
            "SL",
        }
    )

    other_exits = (
        total_closed
        - target_exits
        - stop_exits
    )

    # ---------------------------------------------------------
    # Direction analysis
    # ---------------------------------------------------------

    direction_stats: dict[str, Any] = {}

    for direction in (
        "BUY",
        "SELL",
    ):

        trades = [
            trade
            for trade in closed_views
            if str(
                trade.get("direction")
                or ""
            ).upper()
            == direction
        ]

        direction_wins = [
            trade
            for trade in trades
            if trade["realized_pnl"] > 0
        ]

        direction_pnl = sum(
            trade["realized_pnl"]
            for trade in trades
        )

        direction_stats[
            direction
        ] = {
            "trades": len(trades),
            "wins": len(direction_wins),
            "losses": (
                len(trades)
                - len(direction_wins)
            ),
            "win_rate": (
                len(direction_wins)
                / len(trades)
                * 100.0
                if trades
                else 0.0
            ),
            "pnl": direction_pnl,
        }

    # ---------------------------------------------------------
    # Instrument analysis
    # ---------------------------------------------------------

    instrument_stats: dict[str, Any] = {}

    for symbol in (
        "CRUDEOILM",
        "GOLDM",
        "SILVERM",
    ):

        trades = [
            trade
            for trade in closed_views
            if _market_symbol(trade)
            == symbol
        ]

        instrument_wins = [
            trade
            for trade in trades
            if trade["realized_pnl"] > 0
        ]

        instrument_pnl = sum(
            trade["realized_pnl"]
            for trade in trades
        )

        instrument_stats[
            symbol
        ] = {
            "trades": len(trades),
            "wins": len(
                instrument_wins
            ),
            "losses": (
                len(trades)
                - len(instrument_wins)
            ),
            "win_rate": (
                len(instrument_wins)
                / len(trades)
                * 100.0
                if trades
                else 0.0
            ),
            "pnl": instrument_pnl,
        }

    observations = _load_observations()

    observation_stats = (
        _observation_metrics(
            observations
        )
    )

    return {
        "market": "MCX",
        "mode": "PAPER",
        "paper_trading": True,

        "updated_at": state.get(
            "updated_at"
        ),

        "status": (
            "ACTIVE"
            if state
            else "WAITING"
        ),

        "summary": {
            "total_trades": total_trades,
            "closed_trades": total_closed,
            "active_positions": len(
                active_views
            ),
            "buy_trades": direction_stats[
                "BUY"
            ]["trades"],
            "sell_trades": direction_stats[
                "SELL"
            ]["trades"],
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": win_rate,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "net_pnl": (
                realized_pnl
                + unrealized_pnl
            ),
            "average_trade": average_trade,
            "max_drawdown": max_drawdown,
            "target_exits": target_exits,
            "stop_loss_exits": stop_exits,
            "other_exits": other_exits,
        },

        "pipeline": {
            "observations": observation_stats[
                "observations"
            ],
            "signals_generated": observation_stats[
                "signals_generated"
            ],
            "qualified_signals": observation_stats[
                "qualified_signals"
            ],
            "paper_trades": total_trades,
        },

        "direction": direction_stats,

        "instruments": instrument_stats,

        "active_positions": active_views,

        "closed_trades": list(
            reversed(
                closed_views
            )
        ),

        "equity_curve": equity_curve,
    }
