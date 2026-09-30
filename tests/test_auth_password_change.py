from backend.accounts.auth_models import User, UserStatus
from backend.accounts.auth_registry import AuthRegistry
from backend.accounts.auth_store import AuthUserStore


def make_user() -> User:
    registry = AuthRegistry()

    return User(
        user_id="user_001",
        username="user001",
        password_hash=registry.hash_password("OldPassword123!"),
        status=UserStatus.ACTIVE,
        created_at="2026-09-30T13:00:00+00:00",
    )


def test_change_password_updates_hash():
    registry = AuthRegistry()
    user = make_user()

    registry.register_user(user)

    updated = registry.change_password(
        "user_001",
        "NewPassword123!",
    )

    assert updated.password_hash != user.password_hash
    assert registry.verify_password(
        "NewPassword123!",
        updated.password_hash,
    )
    assert not registry.verify_password(
        "OldPassword123!",
        updated.password_hash,
    )


def test_change_password_persists():
    from pathlib import Path
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "users.json"

        registry = AuthRegistry(
            store=AuthUserStore(path)
        )

        registry.register_user(
            make_user()
        )

        registry.change_password(
            "user_001",
            "NewPassword123!",
        )

        reloaded = AuthRegistry(
            store=AuthUserStore(path)
        )

        user = reloaded.get_user(
            "user_001"
        )

        assert reloaded.verify_password(
            "NewPassword123!",
            user.password_hash,
        )
        assert not reloaded.verify_password(
            "OldPassword123!",
            user.password_hash,
        )


def test_change_password_unknown_user():
    registry = AuthRegistry()

    try:
        registry.change_password(
            "missing_user",
            "NewPassword123!",
        )
    except KeyError as exc:
        assert "missing_user" in str(exc)
    else:
        raise AssertionError(
            "Expected KeyError"
        )
