"""
RUSI Trader AI

Account execution context.

The context identifies which logical account owns an operation.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.accounts.account_models import (
    AccountExecutionMode,
    AccountRole,
)


@dataclass(frozen=True)
class AccountContext:
    """
    Request/runtime context for one RUSI account.

    This intentionally contains identity and execution mode only.
    Secrets and broker tokens must never be carried here.
    """

    account_id: str
    user_id: str

    role: AccountRole = AccountRole.USER

    execution_mode: AccountExecutionMode = (
        AccountExecutionMode.PAPER
    )

    def is_admin(self) -> bool:
        return self.role == AccountRole.ADMIN

    def is_paper(self) -> bool:
        return (
            self.execution_mode
            == AccountExecutionMode.PAPER
        )
