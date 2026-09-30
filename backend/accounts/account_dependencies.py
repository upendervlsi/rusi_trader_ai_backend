"""
RUSI Trader AI

Account authentication dependencies.

Phase 3C:
    - Resolve the account belonging to the authenticated user.
    - Build an AccountContext for request/runtime use.
    - Never accept account ownership from request parameters.
    - No broker credentials.
    - No broker tokens.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from backend.accounts.account_context import AccountContext
from backend.accounts.account_models import Account
from backend.accounts.account_registry import AccountRegistry
from backend.accounts.account_store import AccountStore
from backend.accounts.auth_dependencies import get_current_user
from backend.accounts.auth_models import User


_account_registry = AccountRegistry(
    store=AccountStore()
)


def get_account_registry() -> AccountRegistry:
    """
    Return the process-level account registry.

    Account configuration is persisted through AccountStore.
    Broker credentials and runtime trading state are not stored here.
    """
    return _account_registry


def get_current_account(
    user: User = Depends(get_current_user),
) -> Account:

    registry = get_account_registry()

    user_accounts = [
        account
        for account in registry.list_accounts()
        if account.user_id == user.user_id
    ]

    if not user_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account is associated with the authenticated user.",
        )

    active_accounts = [
        account
        for account in user_accounts
        if account.is_active()
    ]

    if not active_accounts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user's account is disabled.",
        )

    if len(active_accounts) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Multiple active accounts require explicit account selection.",
        )

    return active_accounts[0]


def get_current_account_context(
    account: Account = Depends(get_current_account),
) -> AccountContext:

    return AccountContext(
        account_id=account.account_id,
        user_id=account.user_id,
        role=account.role,
        execution_mode=account.execution_mode,
    )
