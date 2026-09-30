"""
RUSI Trader AI

FastAPI authentication dependencies.

Phase 3B-1:
    - Resolve an authenticated user from a Bearer session token.
    - Convert authentication failure into HTTP 401.
    - No trading endpoint integration yet.
    - No broker credentials.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from backend.accounts.auth_models import (
    User,
)
from backend.accounts.auth_registry import (
    AuthRegistry,
)


_bearer_scheme = HTTPBearer(
    auto_error=False
)

_auth_registry = AuthRegistry()


def get_auth_registry() -> AuthRegistry:
    """
    Return the process-level authentication registry.

    Phase 3B-1 keeps authentication in memory.
    """
    return _auth_registry


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        _bearer_scheme
    ),
) -> User:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    session_id = credentials.credentials.strip()

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication session.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    registry = get_auth_registry()

    try:
        session = registry.get_session(
            session_id
        )

        return registry.get_user(
            session.user_id
        )

    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication session.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )
