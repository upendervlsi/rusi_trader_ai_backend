"""
RUSI Trader AI

Account registry.

Phase 3B-5:
    - Thread-safe account registry.
    - Optional persistent account store.
    - No broker credentials.
    - No broker tokens.
    - No trading operations.
"""

from __future__ import annotations

from threading import RLock

from backend.accounts.account_models import Account
from backend.accounts.account_store import AccountStore


class AccountRegistry:

    def __init__(
        self,
        store: AccountStore | None = None,
    ) -> None:

        self._lock = RLock()
        self._accounts: dict[str, Account] = {}
        self._store = store

        if self._store is not None:
            self._load_persisted_accounts()

    def _load_persisted_accounts(self) -> None:

        accounts = self._store.load_accounts()

        for account in accounts:
            self.register(
                account,
                persist=False,
            )

    def register(
        self,
        account: Account,
        persist: bool = True,
    ) -> Account:
        """
        Register a new account.

        Duplicate account IDs are rejected deliberately.
        """

        if not account.account_id:
            raise ValueError(
                "account_id cannot be empty."
            )

        if not account.user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        with self._lock:

            if account.account_id in self._accounts:
                raise ValueError(
                    f"Account already exists: "
                    f"{account.account_id}"
                )

            self._accounts[
                account.account_id
            ] = account

            if (
                persist
                and self._store is not None
            ):
                self._store.save_accounts(
                    list(self._accounts.values())
                )

        return account

    def get(
        self,
        account_id: str,
    ) -> Account:

        if not account_id:
            raise ValueError(
                "account_id cannot be empty."
            )

        with self._lock:

            account = self._accounts.get(
                account_id
            )

        if account is None:
            raise KeyError(
                f"Account not found: {account_id}"
            )

        return account

    def exists(
        self,
        account_id: str,
    ) -> bool:

        with self._lock:
            return account_id in self._accounts

    def list_accounts(self) -> list[Account]:

        with self._lock:
            return list(
                self._accounts.values()
            )

    def remove(
        self,
        account_id: str,
    ) -> None:

        with self._lock:

            if account_id not in self._accounts:
                raise KeyError(
                    f"Account not found: {account_id}"
                )

            del self._accounts[account_id]

    def clear(self) -> None:

        with self._lock:
            self._accounts.clear()
