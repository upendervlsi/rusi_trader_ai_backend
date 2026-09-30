from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.accounts.auth_dependencies import (
    get_auth_registry,
    get_current_user,
)
from backend.accounts.auth_models import (
    User,
)


def setup_function():

    get_auth_registry().clear()


def teardown_function():

    get_auth_registry().clear()


def make_app() -> FastAPI:

    app = FastAPI()

    @app.get("/protected")
    def protected(
        user: User = __import__(
            "fastapi"
        ).Depends(get_current_user),
    ):
        return {
            "user_id": user.user_id,
            "username": user.username,
        }

    return app


def register_user():

    registry = get_auth_registry()

    registry.register_user(
        User(
            user_id="user_001",
            username="user001",
            password_hash=registry.hash_password(
                "Secret-123!"
            ),
        )
    )


def test_missing_authentication_returns_401():

    register_user()

    client = TestClient(
        make_app()
    )

    response = client.get(
        "/protected"
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Authentication required."
    )


def test_invalid_session_returns_401():

    register_user()

    client = TestClient(
        make_app()
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization":
            "Bearer invalid-session"
        },
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Invalid or expired authentication session."
    )


def test_valid_session_resolves_user():

    register_user()

    registry = get_auth_registry()

    session = registry.authenticate(
        "user001",
        "Secret-123!",
    )

    client = TestClient(
        make_app()
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization":
            f"Bearer {session.session_id}"
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "user_id": "user_001",
        "username": "user001",
    }


def test_logout_invalidates_session():

    register_user()

    registry = get_auth_registry()

    session = registry.authenticate(
        "user001",
        "Secret-123!",
    )

    registry.logout(
        session.session_id
    )

    client = TestClient(
        make_app()
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization":
            f"Bearer {session.session_id}"
        },
    )

    assert response.status_code == 401
