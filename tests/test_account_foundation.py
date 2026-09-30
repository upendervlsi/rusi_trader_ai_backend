from backend.accounts.account_context import (
    AccountContext,
)
from backend.accounts.account_models import (
    Account,
    AccountExecutionMode,
    AccountRole,
)
from backend.accounts.account_registry import (
    AccountRegistry,
)


def make_account(index: int) -> Account:
    return Account(
        account_id=f"account_{index:03d}",
        user_id=f"user_{index:03d}",
        display_name=f"User {index}",
        execution_mode=AccountExecutionMode.PAPER,
    )


def test_register_and_get_account():

    registry = AccountRegistry()

    account = make_account(1)

    registry.register(account)

    loaded = registry.get(
        "account_001"
    )

    assert loaded.account_id == "account_001"
    assert loaded.user_id == "user_001"
    assert loaded.is_active()
    assert loaded.is_paper()


def test_duplicate_account_is_rejected():

    registry = AccountRegistry()

    registry.register(
        make_account(1)
    )

    try:
        registry.register(
            make_account(1)
        )
        assert False, (
            "Duplicate account should fail"
        )
    except ValueError:
        pass


def test_multiple_accounts_are_isolated():

    registry = AccountRegistry()

    account_a = make_account(1)
    account_b = make_account(2)

    registry.register(account_a)
    registry.register(account_b)

    loaded_a = registry.get(
        "account_001"
    )
    loaded_b = registry.get(
        "account_002"
    )

    assert loaded_a.account_id != (
        loaded_b.account_id
    )

    assert loaded_a.user_id != (
        loaded_b.user_id
    )


def test_registry_scales_without_fixed_user_count():

    registry = AccountRegistry()

    for index in range(1, 101):
        registry.register(
            make_account(index)
        )

    accounts = registry.list_accounts()

    assert len(accounts) == 100

    assert registry.exists(
        "account_001"
    )

    assert registry.exists(
        "account_100"
    )


def test_account_context_isolated():

    context_a = AccountContext(
        account_id="account_001",
        user_id="user_001",
        role=AccountRole.USER,
        execution_mode=AccountExecutionMode.PAPER,
    )

    context_b = AccountContext(
        account_id="account_002",
        user_id="user_002",
        role=AccountRole.USER,
        execution_mode=AccountExecutionMode.PAPER,
    )

    assert context_a.account_id != (
        context_b.account_id
    )

    assert context_a.user_id != (
        context_b.user_id
    )

    assert context_a.is_paper()
    assert context_b.is_paper()


def test_admin_context():

    context = AccountContext(
        account_id="admin_001",
        user_id="admin_001",
        role=AccountRole.ADMIN,
        execution_mode=AccountExecutionMode.PAPER,
    )

    assert context.is_admin()
    assert context.is_paper()
