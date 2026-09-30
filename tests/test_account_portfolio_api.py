from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.accounts.account_context import AccountContext
from backend.accounts.account_dependencies import get_current_account
from backend.accounts.account_dependencies import get_current_account_context
from backend.accounts.account_models import Account
from backend.accounts.account_models import AccountExecutionMode
from backend.accounts.account_models import AccountRole
from backend.api.account_portfolio import (
    get_account_portfolio_status,
    router,
)


def make_account() -> Account:
    return Account(
        account_id="account_api_test",
        user_id="user_api_test",
        display_name="API Test Account",
        role=AccountRole.USER,
        execution_mode=AccountExecutionMode.PAPER,
        initial_capital=250000.0,
    )


def make_context(account: Account) -> AccountContext:
    return AccountContext(
        account_id=account.account_id,
        user_id=account.user_id,
        role=account.role,
        execution_mode=account.execution_mode,
    )


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def test_account_portfolio_status_is_account_scoped():
    account = make_account()
    context = make_context(account)

    app = create_app()

    app.dependency_overrides[get_current_account] = lambda: account
    app.dependency_overrides[get_current_account_context] = lambda: context

    client = TestClient(app)

    response = client.get("/api/account/portfolio/status")

    assert response.status_code == 200

    data = response.json()

    assert data["account_id"] == "account_api_test"
    assert data["user_id"] == "user_api_test"
    assert data["role"] == "USER"
    assert data["execution_mode"] == "PAPER"
    assert data["initial_capital"] == 250000.0
    assert data["capital"] == 250000.0
    assert data["available_capital"] == 250000.0
    assert data["open_trades"] == 0
    assert data["closed_trades"] == 0


def test_account_portfolio_status_does_not_accept_account_override():
    account = make_account()
    context = make_context(account)

    app = create_app()

    app.dependency_overrides[get_current_account] = lambda: account
    app.dependency_overrides[get_current_account_context] = lambda: context

    client = TestClient(app)

    response = client.get(
        "/api/account/portfolio/status?account_id=another_account"
    )

    assert response.status_code == 200
    assert response.json()["account_id"] == "account_api_test"


def test_account_portfolio_service_dependency_is_used():
    account = make_account()
    context = make_context(account)

    app = create_app()

    app.dependency_overrides[get_current_account] = lambda: account
    app.dependency_overrides[get_current_account_context] = lambda: context

    client = TestClient(app)

    first = client.get("/api/account/portfolio/status")
    second = client.get("/api/account/portfolio/status")

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["capital"] == second.json()["capital"]
