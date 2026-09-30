from backend.accounts.auth_models import (
    User,
    UserStatus,
)
from backend.accounts.auth_registry import (
    AuthRegistry,
)


def make_user(index: int) -> User:
    registry = AuthRegistry()

    password_hash = registry.hash_password(
        f"Password-{index}-Secure!"
    )

    return User(
        user_id=f"user_{index:03d}",
        username=f"user_{index:03d}",
        password_hash=password_hash,
    )


def test_password_hash_is_not_plaintext():

    registry = AuthRegistry()

    password_hash = registry.hash_password(
        "Secret-123!"
    )

    assert password_hash != "Secret-123!"
    assert password_hash.startswith(
        "pbkdf2_sha256$"
    )


def test_password_verification():

    registry = AuthRegistry()

    password_hash = registry.hash_password(
        "Secret-123!"
    )

    assert registry.verify_password(
        "Secret-123!",
        password_hash,
    )

    assert not registry.verify_password(
        "Wrong-Password!",
        password_hash,
    )


def test_register_and_authenticate_user():

    registry = AuthRegistry()

    password_hash = registry.hash_password(
        "Secret-123!"
    )

    user = User(
        user_id="user_001",
        username="Upender",
        password_hash=password_hash,
    )

    registry.register_user(user)

    session = registry.authenticate(
        "upender",
        "Secret-123!",
    )

    assert session.user_id == "user_001"
    assert session.session_id


def test_username_is_case_insensitive():

    registry = AuthRegistry()

    user = make_user(1)

    registry.register_user(user)

    session = registry.authenticate(
        "USER_001",
        "Password-1-Secure!",
    )

    assert session.user_id == "user_001"


def test_invalid_password_is_rejected():

    registry = AuthRegistry()

    user = make_user(1)

    registry.register_user(user)

    try:
        registry.authenticate(
            "user_001",
            "Wrong-Password!",
        )
        assert False, (
            "Invalid password should fail"
        )
    except ValueError:
        pass


def test_duplicate_user_and_username_are_rejected():

    registry = AuthRegistry()

    registry.register_user(
        make_user(1)
    )

    try:
        registry.register_user(
            make_user(1)
        )
        assert False, (
            "Duplicate user should fail"
        )
    except ValueError:
        pass

    duplicate_username = User(
        user_id="different_user",
        username="USER_001",
        password_hash=registry.hash_password(
            "Another-123!"
        ),
    )

    try:
        registry.register_user(
            duplicate_username
        )
        assert False, (
            "Duplicate username should fail"
        )
    except ValueError:
        pass


def test_disabled_user_cannot_authenticate():

    registry = AuthRegistry()

    user = User(
        user_id="user_disabled",
        username="disabled",
        password_hash=registry.hash_password(
            "Secret-123!"
        ),
        status=UserStatus.DISABLED,
    )

    registry.register_user(user)

    try:
        registry.authenticate(
            "disabled",
            "Secret-123!",
        )
        assert False, (
            "Disabled user should fail"
        )
    except ValueError as exc:
        assert str(exc) == (
            "User account is disabled."
        )


def test_session_resolution_and_logout():

    registry = AuthRegistry()

    user = make_user(1)

    registry.register_user(user)

    session = registry.authenticate(
        "user_001",
        "Password-1-Secure!",
    )

    loaded = registry.get_session(
        session.session_id
    )

    assert loaded.user_id == "user_001"

    registry.logout(
        session.session_id
    )

    try:
        registry.get_session(
            session.session_id
        )
        assert False, (
            "Logged-out session should fail"
        )
    except KeyError:
        pass


def test_multiple_users_are_isolated():

    registry = AuthRegistry()

    for index in range(1, 101):
        registry.register_user(
            make_user(index)
        )

    users = registry.list_users()

    assert len(users) == 100

    session_a = registry.authenticate(
        "user_001",
        "Password-1-Secure!",
    )

    session_b = registry.authenticate(
        "user_100",
        "Password-100-Secure!",
    )

    assert session_a.user_id != (
        session_b.user_id
    )
