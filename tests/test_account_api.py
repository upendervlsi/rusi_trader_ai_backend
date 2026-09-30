from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.accounts.account_context import AccountContext
from backend.accounts.account_dependencies import (
    get_current_account_context,
)
from backend.accounts.account_models import (
    AccountExecutionMode,
    AccountRole,
)
from backend.api.account import router


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def test_account_me_returns_authenticated_account_context():
    app = create_test_app()

    app.dependency_overrides[
        get_current_account_context
    ] = lambda: AccountContext(
        account_id="upender477",
        user_id="rusi_dev_1",
        role=AccountRole.ADMIN,
        execution_mode=AccountExecutionMode.PAPER,
    )

    client = TestClient(app)

    response = client.get("/api/account/me")

    assert response.status_code == 200
    assert response.json() == {
        "account_id": "upender477",
        "user_id": "rusi_dev_1",
        "role": "ADMIN",
        "execution_mode": "PAPER",
    }


def test_account_me_does_not_accept_account_id_from_query():
    app = create_test_app()

    app.dependency_overrides[
        get_current_account_context
    ] = lambda: AccountContext(
        account_id="upender477",
        user_id="rusi_dev_1",
        role=AccountRole.ADMIN,
        execution_mode=AccountExecutionMode.PAPER,
    )

    client = TestClient(app)

    response = client.get(
        "/api/account/me?account_id=another_account"
    )

    assert response.status_code == 200
    assert response.json()["account_id"] == "upender477"
