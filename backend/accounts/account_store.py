"""
RUSI Trader AI

Persistent account store.

Phase 3B-5:
    - Persist logical Account records.
    - No broker credentials.
    - No broker tokens.
    - No portfolio state.
    - Atomic file replacement.
    - File permissions restricted to owner.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock

from backend.accounts.account_models import (
    Account,
    AccountBroker,
    AccountExecutionMode,
    AccountRole,
    AccountStatus,
)


class AccountStore:

    def __init__(
        self,
        path: str | Path = "data/auth/accounts.json",
    ) -> None:

        self._path = Path(path)
        self._lock = RLock()

    def load_accounts(self) -> list[Account]:

        with self._lock:

            if not self._path.exists():
                return []

            with self._path.open(
                "r",
                encoding="utf-8",
            ) as handle:
                payload = json.load(handle)

            if not isinstance(payload, list):
                raise ValueError(
                    "Account store must contain a JSON list."
                )

            accounts: list[Account] = []

            for item in payload:

                if not isinstance(item, dict):
                    raise ValueError(
                        "Invalid account record."
                    )

                accounts.append(
                    Account(
                        account_id=str(
                            item["account_id"]
                        ),
                        user_id=str(
                            item["user_id"]
                        ),
                        display_name=str(
                            item["display_name"]
                        ),
                        role=AccountRole(
                            item.get(
                                "role",
                                AccountRole.USER.value,
                            )
                        ),
                        status=AccountStatus(
                            item.get(
                                "status",
                                AccountStatus.ACTIVE.value,
                            )
                        ),
                        broker=AccountBroker(
                            item.get(
                                "broker",
                                AccountBroker.ANGEL_ONE.value,
                            )
                        ),
                        execution_mode=AccountExecutionMode(
                            item.get(
                                "execution_mode",
                                AccountExecutionMode.PAPER.value,
                            )
                        ),
                        initial_capital=float(
                            item.get(
                                "initial_capital",
                                100000.0,
                            )
                        ),
                        created_at=str(
                            item["created_at"]
                        ),
                        metadata=dict(
                            item.get(
                                "metadata",
                                {},
                            )
                        ),
                    )
                )

            return accounts

    def save_accounts(
        self,
        accounts: list[Account],
    ) -> None:

        with self._lock:

            self._path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            payload = []

            for account in accounts:

                payload.append(
                    {
                        "account_id":
                            account.account_id,
                        "user_id":
                            account.user_id,
                        "display_name":
                            account.display_name,
                        "role":
                            account.role.value,
                        "status":
                            account.status.value,
                        "broker":
                            account.broker.value,
                        "execution_mode":
                            account.execution_mode.value,
                        "initial_capital":
                            account.initial_capital,
                        "created_at":
                            account.created_at,
                        "metadata":
                            dict(account.metadata),
                    }
                )

            temp_path = self._path.with_suffix(
                self._path.suffix + ".tmp"
            )

            with temp_path.open(
                "w",
                encoding="utf-8",
            ) as handle:

                json.dump(
                    payload,
                    handle,
                    indent=2,
                    sort_keys=True,
                )

                handle.write("\n")

            os.chmod(
                temp_path,
                0o600,
            )

            os.replace(
                temp_path,
                self._path,
            )

            os.chmod(
                self._path,
                0o600,
            )
