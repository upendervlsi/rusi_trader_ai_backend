from pathlib import Path

from backend.accounts.account_models import (
    Account,
    AccountExecutionMode,
    AccountRole,
)
from backend.accounts.account_store import (
    AccountStore,
)


def make_account(index: int) -> Account:
    return Account(
        account_id=f"account_{index:03d}",
        user_id=f"user_{index:03d}",
        display_name=f"User {index}",
        role=AccountRole.ADMIN
        if index == 1
        else AccountRole.USER,
        execution_mode=AccountExecutionMode.PAPER,
        initial_capital=100000.0 + index,
    )


def test_missing_store_returns_empty(
    tmp_path: Path,
):

    store = AccountStore(
        tmp_path / "auth" / "accounts.json"
    )

    assert store.load_accounts() == []


def test_save_and_load_accounts(
    tmp_path: Path,
):

    path = (
        tmp_path
        / "auth"
        / "accounts.json"
    )

    store = AccountStore(path)

    accounts = [
        make_account(1),
        make_account(2),
    ]

    store.save_accounts(accounts)

    loaded = store.load_accounts()

    assert len(loaded) == 2

    assert loaded[0].account_id == "account_001"
    assert loaded[0].user_id == "user_001"
    assert loaded[0].role == AccountRole.ADMIN
    assert loaded[0].is_paper()

    assert loaded[1].account_id == "account_002"
    assert loaded[1].role == AccountRole.USER


def test_account_store_preserves_configuration(
    tmp_path: Path,
):

    path = (
        tmp_path
        / "auth"
        / "accounts.json"
    )

    store = AccountStore(path)

    account = Account(
        account_id="account_001",
        user_id="user_001",
        display_name="Admin",
        role=AccountRole.ADMIN,
        execution_mode=AccountExecutionMode.PAPER,
        initial_capital=250000.0,
        metadata={
            "environment": "DEV",
        },
    )

    store.save_accounts([account])

    loaded = store.load_accounts()[0]

    assert loaded.initial_capital == 250000.0
    assert loaded.metadata == {
        "environment": "DEV",
    }


def test_account_store_permissions(
    tmp_path: Path,
):

    path = (
        tmp_path
        / "auth"
        / "accounts.json"
    )

    store = AccountStore(path)

    store.save_accounts(
        [make_account(1)]
    )

    assert path.stat().st_mode & 0o777 == 0o600


def test_account_store_contains_no_broker_credentials(
    tmp_path: Path,
):

    path = (
        tmp_path
        / "auth"
        / "accounts.json"
    )

    store = AccountStore(path)

    store.save_accounts(
        [make_account(1)]
    )

    content = path.read_text(
        encoding="utf-8"
    )

    assert "ANGEL_PASSWORD" not in content
    assert "ANGEL_API_KEY" not in content
    assert "ANGEL_TOTP_SECRET_KEY" not in content
    assert "access_token" not in content
    assert "refresh_token" not in content


def test_registry_persists_and_reloads_accounts(
    tmp_path: Path,
):

    from backend.accounts.account_registry import (
        AccountRegistry,
    )

    path = (
        tmp_path
        / "auth"
        / "accounts.json"
    )

    first_registry = AccountRegistry(
        store=AccountStore(path)
    )

    first_registry.register(
        make_account(1)
    )

    restarted_registry = AccountRegistry(
        store=AccountStore(path)
    )

    loaded = restarted_registry.get(
        "account_001"
    )

    assert loaded.user_id == "user_001"
    assert loaded.role == AccountRole.ADMIN
    assert loaded.is_paper()
    assert loaded.initial_capital == 100001.0
