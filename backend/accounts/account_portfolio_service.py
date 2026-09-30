"""
RUSI Trader AI

Account-scoped paper portfolio access.

Phase 3D-1:
    - Resolve the portfolio belonging to an account.
    - Create the portfolio from account initial capital when needed.
    - Keep portfolio ownership account-scoped.
    - No broker credentials.
    - No broker tokens.
    - No trading execution changes.
"""

from __future__ import annotations

from intelligence.paper_trading.paper_portfolio import PaperPortfolio

from backend.accounts.account_models import Account
from backend.accounts.account_portfolio_registry import (
    AccountPortfolioRegistry,
)


class AccountPortfolioService:

    def __init__(
        self,
        registry: AccountPortfolioRegistry | None = None,
    ) -> None:

        self._registry = (
            registry
            if registry is not None
            else AccountPortfolioRegistry()
        )

    def get_portfolio(
        self,
        account: Account,
    ) -> PaperPortfolio:

        if not account.is_active():
            raise ValueError(
                "Account is disabled."
            )

        return self._registry.get_or_create(
            account_id=account.account_id,
            initial_capital=account.initial_capital,
        )

    def get_registry(
        self,
    ) -> AccountPortfolioRegistry:

        return self._registry
