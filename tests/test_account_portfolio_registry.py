from __future__ import annotations

import pytest

from backend.accounts.account_portfolio_registry import (
    AccountPortfolioRegistry,
)


def test_create_and_get_portfolio():

    registry = AccountPortfolioRegistry()

    portfolio = registry.create(
        "ACC001",
        100000.0,
    )

    assert portfolio.capital == 100000.0
    assert portfolio.available_capital == 100000.0

    assert registry.get("ACC001") is portfolio


def test_duplicate_portfolio_rejected():

    registry = AccountPortfolioRegistry()

    registry.create(
        "ACC001",
        100000.0,
    )

    with pytest.raises(ValueError):
        registry.create(
            "ACC001",
            200000.0,
        )


def test_accounts_have_isolated_portfolios():

    registry = AccountPortfolioRegistry()

    account_a = registry.create(
        "ACC_A",
        100000.0,
    )

    account_b = registry.create(
        "ACC_B",
        200000.0,
    )

    account_a.realized_pnl = 5000.0
    account_a.open_trades.append("TRADE_A")

    assert account_b.realized_pnl == 0.0
    assert account_b.open_trades == []

    assert account_a is not account_b


def test_get_or_create_reuses_existing_portfolio():

    registry = AccountPortfolioRegistry()

    first = registry.get_or_create(
        "ACC001",
        100000.0,
    )

    first.realized_pnl = 2500.0

    second = registry.get_or_create(
        "ACC001",
        500000.0,
    )

    assert second is first
    assert second.capital == 100000.0
    assert second.realized_pnl == 2500.0


def test_missing_portfolio_rejected():

    registry = AccountPortfolioRegistry()

    with pytest.raises(KeyError):
        registry.get("UNKNOWN")


def test_negative_capital_rejected():

    registry = AccountPortfolioRegistry()

    with pytest.raises(ValueError):
        registry.create(
            "ACC001",
            -1.0,
        )


def test_multiple_accounts():

    registry = AccountPortfolioRegistry()

    for index in range(100):

        registry.create(
            f"ACC_{index:03d}",
            100000.0,
        )

    assert len(
        registry.list_account_ids()
    ) == 100
