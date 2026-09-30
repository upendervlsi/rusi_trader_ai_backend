"""
RUSI Trader AI

Account registry.

Phase 1 implementation:
    - In-process account registry.
    - Thread safe.
    - No authentication.
    - No broker credentials.
    - No trading operations.

Persistence/authentication will be introduced in later phases.
"""

from __future__ import annotations

from threading import RLock

from backend.accounts.account_models import Account


class AccountRegistry:

    def __init__(self) -> None:
        self._lock = RLock()
        self._accounts: dict[str, Account] = {}

    def register(self, account: Account) -> Account:
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
