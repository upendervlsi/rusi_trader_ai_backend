from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.accounts.auth_dependencies import get_auth_registry
from backend.accounts.auth_models import User
from backend.api.auth import router


def setup_function():
    get_auth_registry().clear()


def teardown_function():
    get_auth_registry().clear()


def make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def register_test_user():
    registry = get_auth_registry()

    user = User(
        user_id="user_001",
        username="user001",
        password_hash=registry.hash_password(
            "Secret-123!"
        ),
    )

    registry.register_user(user)


def test_login_success():
    register_test_user()

    client = TestClient(make_app())

    response = client.post(
        "/api/auth/login",
        json={
            "username": "user001",
            "password": "Secret-123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == "user_001"
    assert data["username"] == "user001"
    assert isinstance(data["session_id"], str)
    assert data["session_id"]


def test_login_wrong_password():
    register_test_user()

    client = TestClient(make_app())

    response = client.post(
        "/api/auth/login",
        json={
            "username": "user001",
            "password": "Wrong-Password!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username or password."
    )


def test_login_unknown_user():
    client = TestClient(make_app())

    response = client.post(
        "/api/auth/login",
        json={
            "username": "unknown",
            "password": "Secret-123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username or password."
    )


def test_login_session_can_authenticate():
    register_test_user()

    registry = get_auth_registry()

    session = registry.authenticate(
        "user001",
        "Secret-123!",
    )

    resolved = registry.get_session(
        session.session_id
    )

    assert resolved.user_id == "user_001"
