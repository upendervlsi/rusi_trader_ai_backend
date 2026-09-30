from backend.accounts.account_models import (
    Account,
    AccountExecutionMode,
    AccountRole,
)
from backend.accounts.account_portfolio_registry import (
    AccountPortfolioRegistry,
)
from backend.accounts.account_portfolio_service import (
    AccountPortfolioService,
)


def make_account(
    account_id: str,
    user_id: str,
    capital: float,
) -> Account:

    return Account(
        account_id=account_id,
        user_id=user_id,
        display_name=account_id,
        role=AccountRole.USER,
        execution_mode=AccountExecutionMode.PAPER,
        initial_capital=capital,
    )


def test_get_portfolio_creates_account_scoped_portfolio():
    registry = AccountPortfolioRegistry()

    service = AccountPortfolioService(
        registry=registry
    )

    account = make_account(
        "account_a",
        "user_a",
        250000.0,
    )

    portfolio = service.get_portfolio(account)

    assert portfolio.capital == 250000.0
    assert portfolio.available_capital == 250000.0
    assert registry.exists("account_a")


def test_get_portfolio_reuses_existing_portfolio():
    registry = AccountPortfolioRegistry()

    service = AccountPortfolioService(
        registry=registry
    )

    account = make_account(
        "account_a",
        "user_a",
        250000.0,
    )

    first = service.get_portfolio(account)

    first.realized_pnl = 5000.0

    second = service.get_portfolio(account)

    assert first is second
    assert second.realized_pnl == 5000.0


def test_different_accounts_have_isolated_portfolios():
    registry = AccountPortfolioRegistry()

    service = AccountPortfolioService(
        registry=registry
    )

    account_a = make_account(
        "account_a",
        "user_a",
        250000.0,
    )

    account_b = make_account(
        "account_b",
        "user_b",
        500000.0,
    )

    portfolio_a = service.get_portfolio(account_a)
    portfolio_b = service.get_portfolio(account_b)

    portfolio_a.realized_pnl = 10000.0

    assert portfolio_a is not portfolio_b
    assert portfolio_a.realized_pnl == 10000.0
    assert portfolio_b.realized_pnl == 0.0
    assert portfolio_a.capital == 250000.0
    assert portfolio_b.capital == 500000.0


def test_disabled_account_cannot_access_portfolio():
    from backend.accounts.account_models import AccountStatus

    registry = AccountPortfolioRegistry()

    service = AccountPortfolioService(
        registry=registry
    )

    account = make_account(
        "disabled_account",
        "user_disabled",
        100000.0,
    )

    account = Account(
        account_id=account.account_id,
        user_id=account.user_id,
        display_name=account.display_name,
        role=account.role,
        status=AccountStatus.DISABLED,
        broker=account.broker,
        execution_mode=account.execution_mode,
        initial_capital=account.initial_capital,
        created_at=account.created_at,
        metadata=account.metadata,
    )

    try:
        service.get_portfolio(account)
        assert False, "Expected disabled account to be rejected"
    except ValueError as exc:
        assert str(exc) == "Account is disabled."
