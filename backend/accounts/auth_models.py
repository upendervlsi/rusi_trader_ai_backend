"""
RUSI Trader AI

Authentication models.

Phase 3A:
    - User identity
    - Secure password-hash representation
    - Authentication session identity

Broker credentials, broker tokens, portfolio state and
trading positions are intentionally NOT stored here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


@dataclass(frozen=True)
class User:
    """
    Logical RUSI user identity.

    Authentication data is represented by a password hash,
    never by a plaintext password.
    """

    user_id: str
    username: str
    password_hash: str

    status: UserStatus = UserStatus.ACTIVE

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE


@dataclass(frozen=True)
class AuthSession:
    """
    In-memory authentication session.

    This identifies an authenticated user. It does not
    contain broker credentials or trading state.
    """

    session_id: str
    user_id: str

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
