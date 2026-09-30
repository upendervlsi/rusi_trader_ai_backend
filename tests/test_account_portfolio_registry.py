from pathlib import Path

from backend.accounts.account_portfolio_registry import (
    AccountPortfolioRegistry,
)
from backend.accounts.account_portfolio_store import (
    AccountPortfolioStore,
)
from intelligence.paper_trading.paper_portfolio import (
    PaperPortfolio,
)


def test_get_or_create_creates_and_persists_portfolio(
    tmp_path: Path,
):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    registry = AccountPortfolioRegistry(
        store=store
    )

    portfolio = registry.get_or_create(
        account_id="account_a",
        initial_capital=250000.0,
    )

    assert portfolio.capital == 250000.0
    assert portfolio.available_capital == 250000.0

    persisted = store.load(
        "account_a"
    )

    assert persisted is not None
    assert persisted.capital == 250000.0
    assert persisted.available_capital == 250000.0


def test_existing_persisted_portfolio_is_restored(
    tmp_path: Path,
):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    original = PaperPortfolio(
        capital=250000.0,
        available_capital=231500.0,
        realized_pnl=18500.0,
    )

    store.save(
        "account_a",
        original,
    )

    registry = AccountPortfolioRegistry(
        store=store
    )

    restored = registry.get_or_create(
        account_id="account_a",
        initial_capital=999999.0,
    )

    assert restored.capital == 250000.0
    assert restored.available_capital == 231500.0
    assert restored.realized_pnl == 18500.0


def test_registry_save_persists_current_mutations(
    tmp_path: Path,
):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    registry = AccountPortfolioRegistry(
        store=store
    )

    portfolio = registry.get_or_create(
        account_id="account_a",
        initial_capital=100000.0,
    )

    portfolio.available_capital = 87500.0
    portfolio.realized_pnl = 12500.0

    registry.save(
        "account_a"
    )

    fresh_registry = AccountPortfolioRegistry(
        store=store
    )

    restored = fresh_registry.get_or_create(
        account_id="account_a",
        initial_capital=100000.0,
    )

    assert restored.available_capital == 87500.0
    assert restored.realized_pnl == 12500.0


def test_in_memory_portfolio_is_reused(
    tmp_path: Path,
):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    registry = AccountPortfolioRegistry(
        store=store
    )

    first = registry.get_or_create(
        account_id="account_a",
        initial_capital=100000.0,
    )

    second = registry.get_or_create(
        account_id="account_a",
        initial_capital=999999.0,
    )

    assert first is second


def test_different_accounts_remain_isolated(
    tmp_path: Path,
):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    registry = AccountPortfolioRegistry(
        store=store
    )

    first = registry.get_or_create(
        account_id="account_a",
        initial_capital=100000.0,
    )

    second = registry.get_or_create(
        account_id="account_b",
        initial_capital=300000.0,
    )

    first.realized_pnl = 5000.0

    registry.save(
        "account_a"
    )

    assert first is not second
    assert second.realized_pnl == 0.0

    restored_a = store.load(
        "account_a"
    )

    restored_b = store.load(
        "account_b"
    )

    assert restored_a is not None
    assert restored_b is not None

    assert restored_a.realized_pnl == 5000.0
    assert restored_b.realized_pnl == 0.0
