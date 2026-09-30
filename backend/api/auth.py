"""
RUSI Trader AI

Authentication API.

Phase 3B-2:
    - Username/password login.
    - Create an authenticated session.
    - Return a session token.
    - No broker credentials.
    - No trading endpoint integration.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from backend.accounts.auth_registry import AuthRegistry
from backend.accounts.auth_dependencies import get_auth_registry


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    session_id: str
    user_id: str
    username: str


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
) -> LoginResponse:

    registry: AuthRegistry = get_auth_registry()

    try:
        session = registry.authenticate(
            request.username,
            request.password,
        )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    user = registry.get_user(session.user_id)

    return LoginResponse(
        session_id=session.session_id,
        user_id=user.user_id,
        username=user.username,
    )
