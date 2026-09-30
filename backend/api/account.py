"""
RUSI Trader AI

Authenticated account API.

Phase 3C:
    - Return the account belonging to the authenticated user.
    - Never accept account ownership from request parameters.
    - No broker credentials.
    - No broker tokens.
    - No trading operations.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from backend.accounts.account_context import AccountContext
from backend.accounts.account_dependencies import (
    get_current_account_context,
)


router = APIRouter(
    prefix="/api/account",
    tags=["Account"],
)


class AccountMeResponse(BaseModel):
    account_id: str
    user_id: str
    role: str
    execution_mode: str


@router.get(
    "/me",
    response_model=AccountMeResponse,
)
def account_me(
    context: AccountContext = Depends(
        get_current_account_context
    ),
) -> AccountMeResponse:

    return AccountMeResponse(
        account_id=context.account_id,
        user_id=context.user_id,
        role=context.role.value,
        execution_mode=context.execution_mode.value,
    )
