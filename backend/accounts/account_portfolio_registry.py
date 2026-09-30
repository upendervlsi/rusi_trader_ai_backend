"""
RUSI Trader AI

Account portfolio registry.

Phase 3E-2:
    Maps each logical RUSI account to its own PaperPortfolio.

Design:
    - One portfolio per account.
    - Thread safe.
    - Persistent account portfolio state.
    - No broker credentials.
    - No authentication.
    - No trading-engine changes.

The existing PaperPortfolio and PaperPortfolioManager remain unchanged.
"""

from __future__ import annotations

from threading import RLock

from intelligence.paper_trading.paper_portfolio import (
    PaperPortfolio,
)

from backend.accounts.account_portfolio_store import (
    AccountPortfolioStore,
)


class AccountPortfolioRegistry:

    def __init__(
        self,
        store: AccountPortfolioStore | None = None,
    ) -> None:

        self._lock = RLock()

        self._portfolios: dict[
            str,
            PaperPortfolio,
        ] = {}

        self._store = (
            store
            if store is not None
            else AccountPortfolioStore()
        )

    def create(
        self,
        account_id: str,
        initial_capital: float,
    ) -> PaperPortfolio:

        if not account_id:
            raise ValueError(
                "account_id cannot be empty."
            )

        if initial_capital < 0:
            raise ValueError(
                "initial_capital cannot be negative."
            )

        with self._lock:

            if account_id in self._portfolios:
                raise ValueError(
                    f"Portfolio already exists: {account_id}"
                )

            portfolio = PaperPortfolio(
                capital=float(initial_capital),
                available_capital=float(initial_capital),
            )

            self._portfolios[
                account_id
            ] = portfolio

            self._store.save(
                account_id,
                portfolio,
            )

            return portfolio

    def get(
        self,
        account_id: str,
    ) -> PaperPortfolio:

        if not account_id:
            raise ValueError(
                "account_id cannot be empty."
            )

        with self._lock:

            portfolio = self._portfolios.get(
                account_id
            )

        if portfolio is None:
            raise KeyError(
                f"Portfolio not found: {account_id}"
            )

        return portfolio

    def get_or_create(
        self,
        account_id: str,
        initial_capital: float,
    ) -> PaperPortfolio:

        if not account_id:
            raise ValueError(
                "account_id cannot be empty."
            )

        if initial_capital < 0:
            raise ValueError(
                "initial_capital cannot be negative."
            )

        with self._lock:

            portfolio = self._portfolios.get(
                account_id
            )

            if portfolio is not None:
                return portfolio

            portfolio = self._store.load(
                account_id
            )

            if portfolio is not None:

                self._portfolios[
                    account_id
                ] = portfolio

                return portfolio

            portfolio = PaperPortfolio(
                capital=float(initial_capital),
                available_capital=float(initial_capital),
            )

            self._portfolios[
                account_id
            ] = portfolio

            self._store.save(
                account_id,
                portfolio,
            )

            return portfolio

    def save(
        self,
        account_id: str,
    ) -> None:

        with self._lock:

            portfolio = self._portfolios.get(
                account_id
            )

            if portfolio is None:
                raise KeyError(
                    f"Portfolio not found: {account_id}"
                )

            self._store.save(
                account_id,
                portfolio,
            )

    def exists(
        self,
        account_id: str,
    ) -> bool:

        with self._lock:
            return account_id in self._portfolios

    def list_account_ids(
        self,
    ) -> list[str]:

        with self._lock:
            return list(
                self._portfolios.keys()
            )

    def remove(
        self,
        account_id: str,
    ) -> None:

        with self._lock:

            if account_id not in self._portfolios:
                raise KeyError(
                    f"Portfolio not found: {account_id}"
                )

            del self._portfolios[
                account_id
            ]

    def clear(
        self,
    ) -> None:

        with self._lock:
            self._portfolios.clear()
