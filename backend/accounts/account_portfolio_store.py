"""
RUSI Trader AI

Persistent account-scoped paper portfolio store.

Phase 3E-1:
    - Persist one paper portfolio per account.
    - Preserve the existing PaperPortfolio / PaperTrade models.
    - No broker credentials.
    - No broker tokens.
    - No trading execution changes.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from intelligence.paper_trading.paper_portfolio import PaperPortfolio
from intelligence.paper_trading.paper_trade import PaperTrade
from intelligence.signals.signal_type import SignalType


class AccountPortfolioStore:

    def __init__(
        self,
        root: str | Path = "data/accounts",
    ) -> None:

        self._root = Path(root)

    def _path(
        self,
        account_id: str,
    ) -> Path:

        if not account_id:
            raise ValueError(
                "account_id must not be empty."
            )

        if (
            "/" in account_id
            or "\\" in account_id
            or account_id in {".", ".."}
        ):
            raise ValueError(
                "Invalid account_id."
            )

        return (
            self._root
            / account_id
            / "portfolio.json"
        )

    @staticmethod
    def _serialize_trade(
        trade: PaperTrade,
    ) -> dict:

        data = asdict(trade)

        data["signal"] = trade.signal.value

        return data

    @staticmethod
    def _deserialize_trade(
        data: dict,
    ) -> PaperTrade:

        def parse_datetime(
            value,
        ) -> datetime | None:

            if not value:
                return None

            if isinstance(value, datetime):
                return value

            return datetime.fromisoformat(
                str(value)
            )

        return PaperTrade(
            signal=SignalType(
                data["signal"]
            ),

            option_symbol=data.get(
                "option_symbol",
                "",
            ),

            option_token=data.get(
                "option_token",
                "",
            ),

            exchange=data.get(
                "exchange",
                "",
            ),

            strike=float(
                data.get(
                    "strike",
                    0.0,
                )
                or 0.0
            ),

            expiry=data.get(
                "expiry",
                "",
            ),

            option_type=data.get(
                "option_type",
                "",
            ),

            entry_price=float(
                data.get(
                    "entry_price",
                    0.0,
                )
                or 0.0
            ),

            quantity=int(
                data.get(
                    "quantity",
                    0,
                )
                or 0
            ),

            stop_loss=float(
                data.get(
                    "stop_loss",
                    0.0,
                )
                or 0.0
            ),

            target_price=float(
                data.get(
                    "target_price",
                    0.0,
                )
                or 0.0
            ),

            status=data.get(
                "status",
                "OPEN",
            ),

            pnl=float(
                data.get(
                    "pnl",
                    0.0,
                )
                or 0.0
            ),

            current_price=float(
                data.get(
                    "current_price",
                    0.0,
                )
                or 0.0
            ),

            reason=data.get(
                "reason",
                "",
            ),

            entry_time=parse_datetime(
                data.get("entry_time")
            ),

            exit_time=parse_datetime(
                data.get("exit_time")
            ),
        )

    def load(
        self,
        account_id: str,
    ) -> PaperPortfolio | None:

        path = self._path(account_id)

        if not path.exists():
            return None

        raw = path.read_text(
            encoding="utf-8"
        )

        data = json.loads(raw)

        if not isinstance(data, dict):
            raise ValueError(
                "Portfolio data must be a JSON object."
            )

        open_trades = [
            self._deserialize_trade(item)
            for item in data.get(
                "open_trades",
                [],
            )
        ]

        closed_trades = [
            self._deserialize_trade(item)
            for item in data.get(
                "closed_trades",
                [],
            )
        ]

        return PaperPortfolio(
            capital=float(
                data["capital"]
            ),

            available_capital=float(
                data["available_capital"]
            ),

            realized_pnl=float(
                data.get(
                    "realized_pnl",
                    0.0,
                )
                or 0.0
            ),

            open_trades=open_trades,

            closed_trades=closed_trades,
        )

    def save(
        self,
        account_id: str,
        portfolio: PaperPortfolio,
    ) -> None:

        path = self._path(account_id)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "capital": portfolio.capital,
            "available_capital": (
                portfolio.available_capital
            ),
            "realized_pnl": (
                portfolio.realized_pnl
            ),
            "open_trades": [
                self._serialize_trade(trade)
                for trade in portfolio.open_trades
            ],
            "closed_trades": [
                self._serialize_trade(trade)
                for trade in portfolio.closed_trades
            ],
        }

        payload = json.dumps(
            data,
            indent=2,
            default=str,
        )

        fd, temporary_path = tempfile.mkstemp(
            prefix=".portfolio-",
            suffix=".tmp",
            dir=path.parent,
        )

        try:
            os.fchmod(
                fd,
                0o600,
            )

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as temporary_file:

                temporary_file.write(
                    payload
                )

                temporary_file.flush()
                os.fsync(
                    temporary_file.fileno()
                )

            os.replace(
                temporary_path,
                path,
            )

            os.chmod(
                path,
                0o600,
            )

        except Exception:
            try:
                os.unlink(
                    temporary_path
                )
            except FileNotFoundError:
                pass

            raise
