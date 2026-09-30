"""
RUSI Trader AI

Authenticated account-scoped portfolio API.

Phase 3E-3:
    - Expose the authenticated account's paper portfolio.
    - Use one persistent account portfolio registry.
    - Read-only.
    - No broker credentials.
    - No broker tokens.
    - No order execution.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.accounts.account_context import AccountContext
from backend.accounts.account_dependencies import (
    get_current_account,
    get_current_account_context,
)
from backend.accounts.account_models import Account
from backend.accounts.account_portfolio_registry import (
    AccountPortfolioRegistry,
)
from backend.accounts.account_portfolio_service import (
    AccountPortfolioService,
)


router = APIRouter(
    prefix="/api/account/portfolio",
    tags=["account-portfolio"],
)


_account_portfolio_registry = AccountPortfolioRegistry()

_account_portfolio_service = AccountPortfolioService(
    registry=_account_portfolio_registry
)


def get_account_portfolio_service() -> AccountPortfolioService:
    return _account_portfolio_service


@router.get("/status")
def get_account_portfolio_status(
    account: Account = Depends(get_current_account),
    context: AccountContext = Depends(
        get_current_account_context
    ),
    service: AccountPortfolioService = Depends(
        get_account_portfolio_service
    ),
):
    portfolio = service.get_portfolio(account)

    return {
        "account_id": context.account_id,
        "user_id": context.user_id,
        "role": context.role.value,
        "execution_mode": context.execution_mode.value,
        "initial_capital": account.initial_capital,
        "capital": portfolio.capital,
        "available_capital": portfolio.available_capital,
        "open_trades": len(portfolio.open_trades),
        "closed_trades": len(portfolio.closed_trades),
    }
