"""
RUSI Trader AI

Account models.

Phase 1:
    Account identity and configuration only.

Broker credentials, authentication tokens, positions and
portfolio state are intentionally NOT stored here yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AccountRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class AccountExecutionMode(str, Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"


class AccountBroker(str, Enum):
    ANGEL_ONE = "ANGEL_ONE"


@dataclass(frozen=True)
class Account:
    """
    Logical RUSI account.

    This represents ownership/context, not the broker session itself.
    """

    account_id: str
    user_id: str
    display_name: str

    role: AccountRole = AccountRole.USER
    status: AccountStatus = AccountStatus.ACTIVE

    broker: AccountBroker = AccountBroker.ANGEL_ONE
    execution_mode: AccountExecutionMode = AccountExecutionMode.PAPER

    initial_capital: float = 100000.0

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    metadata: dict[str, str] = field(
        default_factory=dict
    )

    def is_active(self) -> bool:
        return self.status == AccountStatus.ACTIVE

    def is_paper(self) -> bool:
        return (
            self.execution_mode
            == AccountExecutionMode.PAPER
        )
