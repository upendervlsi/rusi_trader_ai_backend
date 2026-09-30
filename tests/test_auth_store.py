from pathlib import Path

from backend.accounts.auth_models import User
from backend.accounts.auth_registry import AuthRegistry
from backend.accounts.auth_store import AuthUserStore


def make_user() -> User:
    registry = AuthRegistry()

    return User(
        user_id="user_001",
        username="user001",
        password_hash=registry.hash_password(
            "Secret-123!"
        ),
    )


def test_missing_store_returns_empty_list(
    tmp_path: Path,
):
    store = AuthUserStore(
        tmp_path / "users.json"
    )

    assert store.load_users() == []


def test_save_and_load_users(
    tmp_path: Path,
):
    path = tmp_path / "auth" / "users.json"

    store = AuthUserStore(path)
    user = make_user()

    store.save_users([user])

    assert path.exists()

    loaded = store.load_users()

    assert len(loaded) == 1
    assert loaded[0] == user


def test_password_hash_is_persisted_not_plaintext(
    tmp_path: Path,
):
    path = tmp_path / "users.json"

    store = AuthUserStore(path)
    user = make_user()

    store.save_users([user])

    content = path.read_text(
        encoding="utf-8"
    )

    assert "Secret-123!" not in content
    assert user.password_hash in content


def test_store_permissions_are_restricted(
    tmp_path: Path,
):
    path = tmp_path / "users.json"

    store = AuthUserStore(path)
    store.save_users([make_user()])

    assert path.stat().st_mode & 0o777 == 0o600


def test_registry_loads_and_persists_users(
    tmp_path: Path,
):
    path = tmp_path / "auth" / "users.json"

    store = AuthUserStore(path)

    registry = AuthRegistry(
        store=store
    )

    user = make_user()

    registry.register_user(user)

    restarted_registry = AuthRegistry(
        store=AuthUserStore(path)
    )

    session = restarted_registry.authenticate(
        "user001",
        "Secret-123!",
    )

    assert session.user_id == "user_001"
